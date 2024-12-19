import asyncio
import os
from dotenv import load_dotenv
from agents.story_orchestrator import StoryOrchestrator

async def main():
    # Load environment variables
    load_dotenv()
    
    # Ensure required API keys are present
    required_keys = ['OPENAI_API_KEY', 'STABILITY_API_KEY']
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    if missing_keys:
        raise ValueError(f"Missing required API keys: {', '.join(missing_keys)}")
    
    # Initialize the story orchestrator
    orchestrator = StoryOrchestrator()
    
    # Get story idea from user
    story_idea = input("Enter your story idea: ")
    
    # Create the story video
    try:
        video_path = await orchestrator.create_story_video(story_idea)
        print(f"\nVideo created successfully! You can find it at: {video_path}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
