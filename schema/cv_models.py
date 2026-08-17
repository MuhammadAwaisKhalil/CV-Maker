from pydantic import BaseModel, Field

class CVGenerationRequest(BaseModel):
    job_title:str = Field(
        description="Target job title to tailor the CV for",
        example=["AI Engineer"]
    )

    job_description:str = Field(
        description="The target job posting description used to optimize CV content.",
        example=["Seeking an AI Engineer experienced in agentic workflows, FastAPI, and MCP."]
    )

    output_filepath:str = Field(
        default="CV_Agent/CV.docx",
        example="CV_Agent/AK.docx",
        description=["Target file path where the generated Word document will be saved."]
    )
