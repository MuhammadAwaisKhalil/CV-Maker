from fastapi import FastAPI, status, HTTPException
from router.auth_router import auth_router
from router.agent_router import agent_router
from fastapi.middleware.cors import CORSMiddleware
from db.database import init_db


app = FastAPI(title="AI CV Creater Server")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

@app.include_router(auth_router)
@app.include_router(agent_router)

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    return {"status":"Ok"}

