import os
from typing import List, Dict
from moviepy.editor import ImageClip, TextClip, CompositeVideoClip, concatenate_videoclips
from gtts import gTTS
from moviepy.editor import AudioFileClip
import tempfile

class VideoCreatorAgent:
    def __init__(self):
        self.output_dir = "output"
        self.temp_dir = tempfile.mkdtemp()
        
    def create(self, story_data: Dict) -> str:
        """
        Creates a video from the story chunks, images, and generates narration.
        Returns the path to the final video.
        """
        clips = []
        
        for i, chunk in enumerate(story_data['chunks']):
            # Create narration for this chunk
            audio_path = os.path.join(self.temp_dir, f"narration_{i}.mp3")
            tts = gTTS(text=chunk['text'], lang='en')
            tts.save(audio_path)
            audio_clip = AudioFileClip(audio_path)
            
            # Create image clip
            img_clip = ImageClip(chunk['image_path'])
            
            # Set duration to match the chunk's specified duration
            img_clip = img_clip.set_duration(chunk['duration'])
            
            # Add text overlay
            txt_clip = TextClip(
                chunk['text'],
                fontsize=24,
                color='white',
                bg_color='rgba(0,0,0,0.5)',
                size=(img_clip.w, None),
                method='caption'
            ).set_duration(chunk['duration'])
            
            # Position text at bottom
            txt_clip = txt_clip.set_position(('center', 'bottom'))
            
            # Combine image and text
            composite = CompositeVideoClip([img_clip, txt_clip])
            
            # Add audio
            composite = composite.set_audio(audio_clip)
            
            clips.append(composite)
        
        # Concatenate all clips
        final_clip = concatenate_videoclips(clips)
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Generate output filename using story title
        output_path = os.path.join(
            self.output_dir,
            f"{story_data['title'].replace(' ', '_').lower()}.mp4"
        )
        
        # Write final video
        final_clip.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            audio_codec='aac'
        )
        
        # Cleanup temporary files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)
        
        return output_path
