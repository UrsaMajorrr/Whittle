from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import requirements

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(requirements.router)

@app.get("/")
def read_root():
    return {"message": "Aerospace Design Agent backend is running."} 