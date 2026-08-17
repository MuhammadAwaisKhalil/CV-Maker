import os
import json
from google import genai
from google.genai import types, Client
from config import settings
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

client = Client(api_key=settings.GEMINI_API_KEY)

def convert_mcp_tool_to_gemini_declaration(mcp_tool):
    return types.FunctionDeclaration(name=mcp_tool.name,
                                    description=mcp_tool.description or "",
                                    parameters=mcp_tool.inputSchema,)

async def run_cv_builder_agent(user_id:int, job_title:str, job_description:str, output_filepath:str)->str:
    server_params = StdioServerParameters(command="python",args=["mcp_server/tool_list.py"],env=dict(os.environ))


    async with stdio_client(server_params) as (read_stream,write_stream):
        async with ClientSession(read_stream, write_stream) as session:

            await session.initialize()

            mcp_tools_list = await session.list_tools()
            