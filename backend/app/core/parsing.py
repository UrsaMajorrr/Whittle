from openai import OpenAI
from typing import Dict, Any, Tuple, List
import json
from .config import settings
from ..models.requirements import Message

client = OpenAI(api_key=settings.openai_api_key)

def chat_with_design_assistant(message: str, history: List[Message]) -> str:
    """Have a conversation with the design assistant about requirements and design approaches."""
    
    # Convert our message history to OpenAI's format
    messages = [
        {"role": "system", "content": """You are an expert engineering design assistant who helps engineers refine and develop their design requirements. 
        
        Your approach should be:
        1. Help understand and clarify the initial requirements
        2. Ask probing questions about missing requirements or constraints
        3. Suggest considerations they might have missed
        4. Offer specific next steps in the design process
        5. Be ready to dive into simulations, analysis, or detailed design when they're ready
        
        Always maintain a collaborative, conversational tone. You're a helpful colleague in the design process."""}
    ]
    
    # Add the conversation history
    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})
    
    # Add the new message
    messages.append({"role": "user", "content": message})
    
    # Get response from OpenAI
    response = client.chat.completions.create(
        model=settings.model_name,
        messages=messages
    )
    
    return response.choices[0].message.content

def parse_aerospace_requirement(requirement: str) -> Tuple[Dict[str, Any], str]:
    """Parse any engineering requirement into structured parameters and conversation."""
    
    # First, get a conversational analysis
    conversation_response = client.chat.completions.create(
        model=settings.model_name,
        messages=[
            {"role": "system", "content": """You are an expert engineering design assistant. 
            Analyze the requirement and explain your thinking about how to approach this design challenge.
            Consider key technical considerations, potential challenges, and design approaches.
            Be concise but insightful. Offer to help the user with the design process. Ask them if they would like to continue with any simulations, or paths forward."""},
            {"role": "user", "content": requirement}
        ]
    )
    
    conversation = conversation_response.choices[0].message.content

    # Then get the structured parameters
    system_prompt = """You are an engineering design assistant that converts natural language requirements into structured parameters.
    Convert engineering requirements into a consistent JSON structure with these fields:
    {
        "domain": "The engineering domain (aerospace, mechanical, electrical, etc.)",
        "objective": {
            "type": "maximize/minimize/target/constrain",
            "metric": "The metric to optimize",
            "value": "Target value if applicable"
        },
        "constraints": {
            "parameter_name": {
                "type": "equality/inequality/range",
                "value": "numerical or categorical value",
                "units": "SI units when applicable"
            }
        },
        "design_type": "The type of component or system to design",
        "additional_parameters": {
            "Any additional domain-specific parameters"
        }
    }"""
    
    params_response = client.chat.completions.create(
        model=settings.model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Convert this engineering requirement into structured parameters: {requirement}"}
        ],
        response_format={ "type": "json_object" }
    )
    
    try:
        content = params_response.choices[0].message.content
        parameters = json.loads(content)
        return parameters, conversation
    except Exception as e:
        return {
            "error": "Failed to parse requirement",
            "details": str(e)
        }, "Error occurred while processing the requirement." 