import os
from typing import List, Dict
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from stability_sdk import client
import io
from PIL import Image
import base64

class ImageGeneratorAgent:
    def __init__(self):
        # Initialize Stability AI client
        self.stability_api = client.StabilityInference(
            key=os.getenv('STABILITY_API_KEY'),
            verbose=True,
        )

    def generate(self, story_chunks: List[Dict]) -> List[Dict]:
        """
        Generates images for each story chunk using Stability AI.
        Returns the original chunks with added image paths.
        """
        for chunk in story_chunks:
            # Generate image
            answers = self.stability_api.generate(
                prompt=chunk['image_prompt'],
                steps=50,
                cfg_scale=7.0,
                width=768,
                height=432,  # 16:9 aspect ratio
                samples=1,
                sampler=generation.SAMPLER_K_DPMPP_2M
            )

            # Process and save the generated image
            for answer in answers:
                img = Image.open(io.BytesIO(answer.artifacts[0].binary))
                
                # Create unique filename based on chunk index
                filename = f"image_{story_chunks.index(chunk)}.png"
                img_path = os.path.join("output", "images", filename)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(img_path), exist_ok=True)
                
                # Save image
                img.save(img_path)
                chunk['image_path'] = img_path

        return story_chunks
