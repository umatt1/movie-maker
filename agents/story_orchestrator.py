from typing import List, Dict
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import SystemMessage
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from .story_generator import StoryGeneratorAgent
from .image_generator import ImageGeneratorAgent
from .video_creator import VideoCreatorAgent

class StoryRequest(BaseModel):
    idea: str = Field(..., description="The initial story idea provided by the user")

class StoryOrchestrator:
    def __init__(self):
        # Initialize sub-agents
        self.story_generator = StoryGeneratorAgent()
        self.image_generator = ImageGeneratorAgent()
        self.video_creator = VideoCreatorAgent()
        
        # Create tools from sub-agents
        self.tools = [
            self._create_story_tool(),
            self._create_image_tool(),
            self._create_video_tool()
        ]
        
        # Initialize the orchestrator agent
        self.agent = self._create_agent()
    
    def _create_story_tool(self) -> BaseTool:
        return BaseTool(
            name="generate_story",
            description="Generates a detailed story split into chunks with image prompts",
            func=self.story_generator.generate,
            args_schema=StoryRequest
        )
    
    def _create_image_tool(self) -> BaseTool:
        return BaseTool(
            name="generate_images",
            description="Generates images based on story chunks and prompts",
            func=self.image_generator.generate,
        )
    
    def _create_video_tool(self) -> BaseTool:
        return BaseTool(
            name="create_video",
            description="Creates a video from images, text, and generates voice narration",
            func=self.video_creator.create,
        )
    
    def _create_agent(self) -> AgentExecutor:
        llm = ChatOpenAI(temperature=0.7, model="gpt-4")
        
        system_message = """You are a creative story-to-video orchestrator. Your goal is to:
1. Take a user's story idea and generate a detailed, engaging 2-minute story
2. Create vivid, whimsical images for each story segment
3. Combine everything into a captivating video with narration
Follow these steps in order and ensure each step is completed before moving to the next."""

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_message),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_openai_functions_agent(llm, self.tools, prompt)
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )
    
    async def create_story_video(self, idea: str) -> str:
        """
        Main entry point to create a story video from an idea.
        Returns the path to the created video.
        """
        result = await self.agent.ainvoke({"input": idea})
        return result["output"]
