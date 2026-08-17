from fastapi  import APIRouter, status, HTTPException, Depends
from fastapi.responses import FileResponse
from schema.cv_models import CVGenerationRequest
from auth.utils import get_current_user_id
from app.cv_agent import run_cv_builder_agent
import os

agent_router = APIRouter(prefix="/agent")

@agent_router.post("/generate_docx", status_code=status.HTTP_201_CREATED)
async def create_cv(payload:CVGenerationRequest, user_id:int = Depends(get_current_user_id)):
    try:
        if payload.output_filepath == "CV_Agent/CV.docx":
            output_path = f"CV_Agent/user_{user_id}_CV.docx"
        else:
            output_path = payload.output_filepath

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        generated_file = await run_cv_builder_agent(user_id,
                                                    job_title=payload.job_title,
                                                    job_description=payload.job_description,
                                                    output_filepath=output_path)

        return FileResponse(
            path=generated_file,
            
            filename=f"CV_{payload.job_title.replace(' ', '_')}.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))

    