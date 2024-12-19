import os
from typing import Dict
from moviepy import editor as mpy
from gtts import gTTS
import tempfile
import json

class VideoCreatorAgent:
    def __init__(self):
        self.output_dir = "outputs"
        os.makedirs(self.output_dir, exist_ok=True)
        self.temp_dir = tempfile.mkdtemp()
        
    def create(self, story_data: Dict) -> str:
        """
        Creates a video from the story chunks, images, and generates narration.
        Returns the path to the final video.
        """
        # Convert string to dict if necessary
        if isinstance(story_data, str):
            story_data = json.loads(story_data)
            
        clips = []
        
        for i, chunk in enumerate(story_data['chunks']):
            # Create narration for this chunk
            audio_path = os.path.join(self.temp_dir, f"narration_{i}.mp3")
            tts = gTTS(text=chunk['text'], lang='en')
            tts.save(audio_path)
            audio_clip = mpy.AudioFileClip(audio_path)
            
            # Create image clip with cross-fade effects
            img_clip = (mpy.ImageClip(chunk['image_path'])
                       .set_duration(audio_clip.duration)
                       .crossfadein(1)
                       .crossfadeout(1))
            
            # Add audio with fade effects
            audio_clip = (audio_clip
                         .audio_fadein(1)
                         .audio_fadeout(1))
            
            # Combine image and audio
            video_clip = img_clip.set_audio(audio_clip)
            
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
                preset='medium'  # Balance between quality and encoding speed
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
