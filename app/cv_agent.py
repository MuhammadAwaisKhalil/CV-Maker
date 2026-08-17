import os
import json
from google import genai
from google.genai import types, Client
from config import settings
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

client = Client(api_key=settings.GEMINI_API_KEY)

def convert_mcp_tool_to_gemini_declaration(mcp_tool):
    schema_dict = mcp_tool.inputSchema if isinstance(mcp_tool.inputSchema, dict) else {}
    return types.FunctionDeclaration(name=mcp_tool.name,
                                    description=mcp_tool.description or "",
                                    parameters=schema_dict)


async def run_cv_builder_agent(user_id:int, job_title:str, job_description:str, output_filepath:str)->str:
    server_params = StdioServerParameters(command="python",args=["mcp_server/tool_list.py"],env=dict(os.environ))


    async with stdio_client(server_params) as (read_stream,write_stream):
        async with ClientSession(read_stream, write_stream) as session:

            await session.initialize()

            mcp_tools_list = await session.list_tools()

            gemini_declarations = [
                convert_mcp_tool_to_gemini_declaration(tool) for tool in mcp_tools_list.tools
            ]

            tool_config = types.Tool(function_declarations=gemini_declarations)

            system_instruction = """
    You are an AI Resume Agent operating over the Model Context Protocol (MCP).

    YOUR WORKFLOW:
    1. Call `get_user_full_context_tool` with `user_id` to retrieve candidate database records.
    2. Analyze candidate data against job requirements and generate a python-docx script.
    3. Call `execute_dynamic_cv_code_tool` with your Python script and `output_filepath`.
    4. RECOVERY LOOP: If execution returns "success": False, inspect the error log, adjust the python-docx script, and call `execute_dynamic_cv_code_tool` again until successful.

    
    """
            chat = client.chats.create(model="gemini-2.5-flash",
                                       config=types.GenerateContentConfig(
                                           system_instruction=system_instruction,
                                           tools=[tool_config],
                                           temperature=0.1
                                       ))

            prompt = f"""
            Generate a custom Word (.docx) CV for:
            - User ID: {user_id}
            - Target Job: {job_title}
            - Job Description: {job_description}
            - Output Filepath: {output_filepath}

            Use the most popular and widely accepted CV format to build the CV for the desired role.
            """

            response = chat.send_message(prompt)

            iteration_count=0

            while iteration_count<settings.MAX_AGENT_ITERATIONS:
                iteration_count+=1
                #If the agent does not want to use anytool after it has done making cv
                if not response.function_calls:
                    break

                function_responses=[]

                #Get functions LLM decided to call upon the iteration
                for function in response.function_calls:
                    fname = function.name
                    fargs = function.args


                    #Call/Execute the tool LLM wants to use
                    tool_result = await session.call_tool(name=fname,arguments=fargs)


                    #Parse the JSON reuslt LLM tool has returned
                    result_text = tool_result.content[0].text if tool_result.content else ""
                    try:
                        parsed_payload = json.loads(result_text)
                    except json.JSONDecodeError:
                        parsed_payload = {"result":result_text}

                    function_responses.append(
                        types.Part.from_function_response(
                            name=fname,
                            response={"result": parsed_payload},
                        )
                    )


                #Send the output feedback as context to llm
                response = chat.send_message(function_responses)
            if not os.path.exists(output_filepath):
                raise RuntimeError(
                        f"Agent failed to generate CV within maximum allowed limit ({settings.MAX_AGENT_ITERATIONS} iterations). "
                        f"Please check code sandbox permissions or script syntax."
                    )

            return output_filepath

                    