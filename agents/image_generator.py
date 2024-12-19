import os
from typing import List, Dict, Union
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from stability_sdk import client
import io
from PIL import Image
import base64
import json

class ImageGeneratorAgent:
    def __init__(self):
        # Initialize Stability AI client
        self.stability_api = client.StabilityInference(
            key=os.getenv('STABILITY_API_KEY'),
            verbose=True,
        )

    def generate(self, story_data: Union[Dict, str, List]) -> Dict:
        """
        Generates images for each story chunk using Stability AI.
        Returns the original story data with added image paths.
        
        Args:
            story_data: Either a dictionary containing story data, a JSON string, or a list
        """
        # Convert string to dict if necessary
        if isinstance(story_data, str):
            story_data = json.loads(story_data)
        
        # If story_data is a list, convert it to the expected dictionary format
        if isinstance(story_data, list):
            story_data = {
                'title': story_data[0],
                'chunks': story_data[1],
                'total_duration': story_data[2]
            }
        
        chunks = story_data['chunks']
        for chunk in chunks:
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
                filename = f"image_{chunks.index(chunk)}.png"
                img_path = os.path.join("output", "images", filename)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(img_path), exist_ok=True)
                
                # Save image
                img.save(img_path)
                chunk['image_path'] = img_path

        return story_data
