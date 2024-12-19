from typing import List, Dict
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import SystemMessage
from langchain.tools import Tool
from pydantic import BaseModel, Field
from .story_generator import StoryGeneratorAgent
from .image_generator import ImageGeneratorAgent
# from .video_creator import VideoCreatorAgent

class StoryRequest(BaseModel):
    idea: str = Field(..., description="The initial story idea provided by the user")

class StoryOrchestrator:
    def __init__(self):
        # Initialize sub-agents
        self.story_generator = StoryGeneratorAgent()
        self.image_generator = ImageGeneratorAgent()
        # self.video_creator = VideoCreatorAgent()
        
        # Create tools from sub-agents
        self.tools = [
            self._create_story_tool(),
            self._create_image_tool(),
            # self._create_video_tool()
        ]
        
        # Initialize the orchestrator agent
        self.agent = self._create_agent()
    
    def _create_story_tool(self) -> Tool:
        return Tool(
            name="generate_story",
            description="Generates a detailed story split into chunks with image prompts",
            func=self.story_generator.generate,
        )
    
    def _create_image_tool(self) -> Tool:
        return Tool(
            name="generate_images",
            description="""Generates images for each story chunk. Input must be the complete story dictionary returned by generate_story.
Do NOT convert the dictionary to a string - pass it exactly as received from generate_story.""",
            func=self.image_generator.generate,
        )
    
    # def _create_video_tool(self) -> Tool:
    #     return Tool(
    #         name="create_video",
    #         description="Creates a video from images, text, and generates voice narration",
    #         func=self.video_creator.create,
    #     )
    
    def _create_agent(self) -> AgentExecutor:
        llm = ChatOpenAI(temperature=0.7, model="gpt-4")
        
        system_message = """You are a creative story-to-video orchestrator. Follow these steps in order:

1. First, use the generate_story tool with the user's story idea to create a detailed story.
   The tool will return a dictionary containing the story chunks and other metadata.

2. Take the COMPLETE dictionary output from generate_story and pass it directly to the generate_images tool.
   Do NOT convert the dictionary to a string or modify it in any way.

Important: Pass the story data between tools exactly as received, maintaining its dictionary format."""

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_message),
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