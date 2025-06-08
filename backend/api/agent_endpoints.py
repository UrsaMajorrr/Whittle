from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from agents.config import CAD_AGENT_CONFIG, MESH_AGENT_CONFIG, SIMULATION_AGENT_CONFIG
from agents.cad_agent import CADAgent
from agents.mesh_agent import MeshAgent
from agents.simulation_agent import SimulationAgent

router = APIRouter()

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[Message]

class ChatResponse(BaseModel):
    response: str

# Initialize agents with their specific configurations
cad_agent = CADAgent(CAD_AGENT_CONFIG)
mesh_agent = MeshAgent(MESH_AGENT_CONFIG)
simulation_agent = SimulationAgent(SIMULATION_AGENT_CONFIG)

@router.post("/agent/cad/chat", response_model=ChatResponse)
async def cad_chat(request: ChatRequest):
    """
    Chat with the CAD agent
    """
    try:
        response = await cad_agent.chat(request.message, request.history)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agent/mesh/chat", response_model=ChatResponse)
async def mesh_chat(request: ChatRequest):
    """
    Chat with the Meshing agent
    """
    try:
        response = await mesh_agent.chat(request.message, request.history)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agent/simulation/chat", response_model=ChatResponse)
async def simulation_chat(request: ChatRequest):
    """
    Chat with the Simulation agent
    """
    try:
        response = await simulation_agent.chat(request.message, request.history)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 