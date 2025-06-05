from fastapi import FastAPI
from app.api import requirements

app = FastAPI()

app.include_router(requirements.router)

@app.get("/")
def read_root():
    return {"message": "Aerospace Design Agent backend is running."} 