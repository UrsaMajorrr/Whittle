from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Optional
from pathlib import Path
import json

from whittle.src.entities.llm_agent import LLMAgent
from whittle.src.entities.cfd_software import CFDSoftware
from whittle.src.application.llm_agent_interactor import OpenAILLMAgent, ClaudeLLMAgent
from whittle.src.application.cfd_interactor import FOAM, SU2

app = FastAPI(title="Whittle API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the directory containing this file
current_dir = Path(__file__).parent
# The static directory should be at the same level as the api directory
static_dir = current_dir.parent.parent / "static"
static_dir.mkdir(exist_ok=True)

# Mount static files (frontend)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/")
async def read_root():
    return FileResponse(str(static_dir / "index.html"))

# Models
class Message(BaseModel):
    content: str
    
class CommandRequest(BaseModel):
    software: str
    command: str
    options: Optional[Dict] = {}

# Global state (in production, use proper state management)
current_llm: Optional[LLMAgent] = None
current_cfd: Optional[CFDSoftware] = None

@app.post("/api/llm/select")
async def select_llm(agent_type: Message):
    global current_llm
    try:
        system_prompt = "You are a helpful CFD assistant"
        if agent_type.content == "GPT-4.1":
            current_llm = OpenAILLMAgent(system_prompt)
        elif agent_type.content == "Claude":
            current_llm = ClaudeLLMAgent(system_prompt)
        else:
            raise HTTPException(status_code=400, detail="Invalid LLM agent type")
        return {"status": "ok", "message": f"Selected {agent_type.content}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cfd/select")
async def select_cfd(software_type: Message):
    global current_cfd
    try:
        if software_type.content == "OpenFOAM":
            current_cfd = FOAM(Path.cwd())
        elif software_type.content == "SU2":
            current_cfd = SU2(Path.cwd())
        else:
            raise HTTPException(status_code=400, detail="Invalid CFD software type")
        return {"status": "ok", "message": f"Selected {software_type.content}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cfd/execute")
async def execute_command(request: CommandRequest):
    if not current_cfd:
        raise HTTPException(status_code=400, detail="No CFD software selected")
    try:
        current_cfd.run_command(request.command, request.options)
        return {"status": "ok", "message": f"Executed command: {request.command}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()
            if not current_llm:
                await websocket.send_json({
                    "error": "No LLM agent selected"
                })
                continue
                
            try:
                # Get streaming response from LLM
                response = current_llm.return_response(message)
                accumulated_content = ""
                
                # Stream each chunk to the client
                try:
                    for event in response:
                        if hasattr(event.choices[0].delta, 'content'):
                            content = event.choices[0].delta.content
                            if content:
                                accumulated_content += content
                                await websocket.send_json({
                                    "type": "chunk",
                                    "content": content
                                })
                    
                    # If we got here, streaming completed successfully
                    await websocket.send_json({
                        "type": "complete"
                    })
                except Exception as stream_error:
                    # If streaming fails partway through, try to send what we have
                    if accumulated_content:
                        await websocket.send_json({
                            "type": "chunk",
                            "content": "\n\n[Error: Message was cut off due to: " + str(stream_error) + "]"
                        })
                    await websocket.send_json({
                        "type": "complete"
                    })
                    print(f"Streaming error: {stream_error}")
                
            except Exception as e:
                error_msg = str(e)
                print(f"LLM error: {error_msg}")
                await websocket.send_json({
                    "error": error_msg
                })
                
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.close()
        except:
            pass 