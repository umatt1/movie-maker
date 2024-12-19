# Story Video Maker

An AI-powered application that transforms story ideas into engaging videos with narration and generated images.

## Features

- Takes a story idea and generates a detailed 2-minute narrative
- Splits the story into chunks with custom image prompts
- Generates unique images for each story segment using Stability AI
- Creates a video with synchronized narration, images, and text overlays
- Fully automated process from story idea to final video

## Prerequisites

- Python 3.8+
- OpenAI API key
- Stability AI API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/story-video-maker.git
cd story-video-maker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys:
```bash
cp example.env .env
```
Then edit `.env` and add your API keys.

## Usage

Run the main script:
```bash
python main.py
```

Enter your story idea when prompted, and the application will:
1. Generate a detailed story
2. Create custom images
3. Produce a video with narration

The final video will be saved in the `output` directory.

## Project Structure

- `agents/`: Contains the main agent components
  - `story_orchestrator.py`: Coordinates the entire process
  - `story_generator.py`: Creates the narrative and image prompts
  - `image_generator.py`: Generates images using Stability AI
  - `video_creator.py`: Assembles the final video
- `main.py`: Entry point of the application
- `requirements.txt`: Python dependencies
- `example.env`: Template for API keys

## License

MIT License
