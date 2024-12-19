from typing import List, Dict
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

class StoryChunk(BaseModel):
    text: str = Field(..., description="The story text for this chunk")
    image_prompt: str = Field(..., description="A prompt to generate an image for this chunk")
    duration: float = Field(..., description="Duration in seconds this chunk should last in the video")

class StoryOutput(BaseModel):
    title: str = Field(..., description="The title of the story")
    chunks: List[StoryChunk] = Field(..., description="List of story chunks with their image prompts")
    total_duration: float = Field(..., description="Total duration of the story in seconds")

class StoryGeneratorAgent:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0.8, model="gpt-4")
        self.output_parser = PydanticOutputParser(pydantic_object=StoryOutput)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a creative story generator that creates engaging, whimsical 2-minute stories. 
            For each story:
            1. Create a compelling narrative that can be told in 2 minutes
            2. Split the story into 4-8 chunks, each with accompanying image prompts
            3. Each chunk should be timed to fit within the 2-minute constraint
            4. Image prompts should be detailed and creative, focusing on key story elements
            5. Ensure the story flows naturally between chunks"""),
            ("human", "Create a 2-minute story based on this idea: {idea}"),
            ("system", "Format your response as a JSON object with the following structure:\n{format_instructions}")
        ])

    def generate(self, idea: str) -> Dict:
        """
        Generates a story with image prompts from an initial idea.
        Returns a dictionary containing the story chunks and metadata.
        """
        formatted_prompt = self.prompt.format_messages(
            idea=idea,
            format_instructions=self.output_parser.get_format_instructions()
        )
        
        response = self.llm.predict_messages(formatted_prompt)
        story_output = self.output_parser.parse(response.content)
        
        # Validate total duration is approximately 120 seconds
        if not 115 <= story_output.total_duration <= 125:
            raise ValueError("Story duration must be approximately 120 seconds")
            
        return story_output.model_dump()
