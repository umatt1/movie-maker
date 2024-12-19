import os
from typing import Dict
from moviepy import editor as mpy
import tempfile
import json
import requests
import time
from textwrap import wrap

class VideoCreatorAgent:
    def __init__(self):
        self.output_dir = "outputs"
        os.makedirs(self.output_dir, exist_ok=True)
        self.temp_dir = tempfile.mkdtemp()
        self.eleven_api_key = os.getenv('ELEVEN_API_KEY')
        # Rachel voice ID - a natural, warm voice good for storytelling
        self.voice_id = "21m00Tcm4TlvDq8ikWAM"
        
    def _generate_audio(self, text: str, filename: str) -> str:
        """Generate natural-sounding narration using ElevenLabs API."""
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.eleven_api_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            return filename
        else:
            raise Exception(f"Audio generation failed: {response.text}")

    def _create_subtitle_clip(self, text: str, duration: float, size: tuple) -> mpy.TextClip:
        """Create a subtitle clip with text wrapped and positioned at the bottom."""
        # Wrap text to fit screen width (approximate characters per line)
        wrapped_text = "\n".join(wrap(text, width=50))
        
        # Create text clip with nice styling
        txt_clip = (mpy.TextClip(
            wrapped_text,
            font='Arial',
            fontsize=30,
            color='white',
            stroke_color='black',
            stroke_width=2,
            size=(size[0] - 40, None),  # Leave margin on sides
            method='caption',
            align='center'
        )
        .set_duration(duration)
        .set_position(('center', 'bottom'))
        .margin(bottom=20, opacity=0))  # Add bottom margin
        
        # Add fade in/out
        txt_clip = txt_clip.crossfadein(0.5).crossfadeout(0.5)
        return txt_clip
        
    def create(self, story_data: Dict) -> str:
        """
        Creates a video from the story chunks, images, and generates narration.
        Returns the path to the final video.
        """
        # Convert string to dict if necessary
        if isinstance(story_data, str):
            story_data = json.loads(story_data)
            
        clips = []
        video_size = (768, 432)  # 16:9 aspect ratio
        
        for i, chunk in enumerate(story_data['chunks']):
            # Create natural narration for this chunk
            audio_path = os.path.join(self.temp_dir, f"narration_{i}.mp3")
            self._generate_audio(chunk['text'], audio_path)
            
            # Add a small delay to prevent rate limiting
            time.sleep(0.5)
            
            audio_clip = mpy.AudioFileClip(audio_path)
            
            # Create image clip with cross-fade effects
            img_clip = (mpy.ImageClip(chunk['image_path'])
                       .set_duration(audio_clip.duration)
                       .crossfadein(0.5)
                       .crossfadeout(0.5))
            
            # Create and position subtitle
            subtitle = self._create_subtitle_clip(
                chunk['text'],
                audio_clip.duration,
                video_size
            )
            
            # Composite image and subtitle
            video_clip = mpy.CompositeVideoClip(
                [img_clip, subtitle],
                size=video_size
            )
            
            # Add audio with gentle fade effects
            audio_clip = audio_clip.audio_fadein(0.3).audio_fadeout(0.3)
            video_clip = video_clip.set_audio(audio_clip)
            
            clips.append(video_clip)
        
        # Concatenate all clips with method='compose' for smoother transitions
        final_clip = mpy.concatenate_videoclips(clips, method='compose')
        
        # Generate output filename using story title
        output_path = os.path.join(
            self.output_dir,
            f"{story_data['title'].replace(' ', '_').lower()}.mp4"
        )
        
        try:
            # Write final video with high quality settings
            final_clip.write_videofile(
                output_path,
                fps=24,
                codec='libx264',
                audio_codec='aac',
                bitrate='8000k',
                audio_bitrate='384k',
                threads=4,
                preset='medium'
            )
        finally:
            # Clean up
            final_clip.close()
            for clip in clips:
                clip.close()
            
            # Remove temporary files
            for file in os.listdir(self.temp_dir):
                os.remove(os.path.join(self.temp_dir, file))
            os.rmdir(self.temp_dir)
        
        return output_path
