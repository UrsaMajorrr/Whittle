from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import requirements
from api.agent_endpoints import router as agent_router

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(requirements.router)
app.include_router(agent_router, prefix="/api")  # Mount agent endpoints under /api prefix

@app.get("/")
def read_root():
    return {"message": "Aerospace Design Agent backend is running."} 