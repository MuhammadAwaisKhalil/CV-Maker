import os
from fastapi import FastAPI, HTTPException, status
from schema.models import CVGenerateRequest
from fastapi.responses import FileResponse
from app.cv_agent import run_cv_agent
from app.docx_generator import create_docx

app = FastAPI(title="AI Resume Creator")

@app.post("/generate_cv")
async def generate_cv(user_id:int, request:CVGenerateRequest):
    try:
        tailored_cv = await run_cv_agent(user_id, request)

        file_path = create_docx(tailored_cv)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Failed to create the document")
        filename = os.path.basename(file_path)

        return FileResponse(
                path=file_path,
                filename=filename,
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during CV generation: {str(e)}",
        )
    