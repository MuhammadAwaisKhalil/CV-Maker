import sys
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from schema.models import CVGenerateRequest,TailoredCVOutput
import json



client = genai.Client()

async def run_cv_agent(user_id:int, request:CVGenerateRequest)->TailoredCVOutput:
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m","mcp_server.server"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            mcp_tools_list = await session.list_tools() 

            gemini_tools = [
                types.Tool(
                    function_declarations=[
                        types.FunctionDeclaration(
                            name=tool.name,
                            description=tool.description,
                            parameters=tool.inputSchema
                        )
                        for tool in mcp_tools_list.tools
                    ]
                )
            ]

            prompt = f"""
            You are an expert ATS CV Optimization Agent.
            
            Task:
            1. Use the database tools to retrieve the full profile data for user_id={user_id}.
            2. Analyze the job requirements for:
               - Target Role: {request.target_job_title}
               - Target Company: {request.target_company or 'N/A'}
               - Job Description: {request.job_description}
            3. Rewrite and tailor the candidate's experience, project bullets, skills, and summary 
               to highlight relevance and key terms from the job description.
            """

            response = await client.aio.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=gemini_tools,
                    temperature=0.2
                )
            )

            chat_messages = [types.Content(role="user", parts=[types.Part.from_text(text=prompt)]),
                             response.candidates[0].content]

            #Tool execution loop
            while response.function_calls:
                tool_responses = []

                for call in response.function_calls:
                    #Execute tool call
                    mcp_result = session.call_tool(call.name, call.args)

                    #Read response text returned by mcp server
                    result_data = json.loads(mcp_result.content[0].text)

                    tool_responses.append(types.Part.from_function_response(
                        name=call.name,
                        response={"result",result_data}
                    ))

                chat_messages.append(types.Content(role="user", parts=tool_responses))


                response = await client.aio.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=chat_messages,
                    config = types.GenerateContentConfig(tools=gemini_tools)
                )

            final_response = await client.aio.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    *chat_messages,
                    types.Content(role="user",parts=types.Part.from_text(text="Synthesize all gathered data and output the final tailored CV matching the required JSON schema."))

                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=TailoredCVOutput,
                )
            )
            return TailoredCVOutput.model_validate_json(final_response.text)




