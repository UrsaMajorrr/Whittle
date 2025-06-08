from typing import List, Optional, Dict, Any
import autogen
from pydantic import BaseModel
import asyncio
from concurrent.futures import ThreadPoolExecutor

class Message(BaseModel):
    role: str
    content: str

class SimulationAgent:
    """Simulation Agent for handling engineering analysis tasks"""
    
    def __init__(self, config: dict):
        """Initialize the Simulation agent with configuration"""
        self.config = config
        self.agent = self._create_agent()
        self._executor = ThreadPoolExecutor(max_workers=1)
        
    def _create_agent(self):
        """Create the AutoGen agent with configuration"""
        config = {
            "name": self.config["name"],
            "llm_config": self.config["llm_config"],
            "system_message": self.config["system_message"],
            "is_termination_msg": lambda x: False,  # Prevent early termination
            "human_input_mode": "NEVER",
            "description": "Simulation Assistant that always responds with role 'assistant'",
        }
        
        # Create a wrapper function to ensure correct message format
        def format_message(msg):
            if isinstance(msg, str):
                return {
                    "role": "assistant",
                    "content": msg,
                    "name": self.config["name"]
                }
            elif isinstance(msg, dict):
                msg["role"] = "assistant"
                msg["name"] = self.config["name"]
                return msg
            return msg

        agent = autogen.AssistantAgent(
            **config,
            default_auto_reply="",  # Empty default reply
        )
        
        # Override the generate_reply method to ensure correct message format
        original_generate = agent.generate_reply
        def generate_reply_wrapper(*args, **kwargs):
            reply = original_generate(*args, **kwargs)
            if reply:
                return format_message(reply)
            return reply
        agent.generate_reply = generate_reply_wrapper
        
        return agent
    
    def _generate_response_sync(self, messages):
        """Synchronously generate response using AutoGen"""
        try:
            print(f"\nProcessing message: {messages[-1]['content']}")
            
            # Create a human proxy agent for the conversation
            human_proxy = autogen.UserProxyAgent(
                name="human_proxy",
                human_input_mode="NEVER",
                max_consecutive_auto_reply=0,
                code_execution_config={
                    "work_dir": "coding",
                    "use_docker": True,
                    "timeout": 60,
                },
                system_message="Proxy for human user. Send messages with the correct role.",
            )
            
            print("\nInitiating chat with agent...")
            # Initialize chat with the last message
            last_message = messages[-1]["content"]
            
            # Create the message with explicit role - this should be 'user' since it's from the human proxy
            user_message = {
                "role": "user",
                "content": last_message,
                "name": "human_proxy"
            }
            
            chat_response = human_proxy.initiate_chat(
                self.agent,
                message=user_message,
                clear_history=True  # Start fresh for each request
            )
            
            print("\nDirect chat response:", chat_response)
            
            print("\nChecking chat messages...")
            # First try to get the direct response
            if isinstance(chat_response, autogen.ChatResult) and chat_response:
                print("Found ChatResult, extracting from chat_history...")
                if chat_response.chat_history:
                    # Get the last message from our agent by checking the name
                    for message in reversed(chat_response.chat_history):
                        if message.get('name') == self.agent.name:
                            # Create a properly formatted response - this should be 'assistant' since it's from our agent
                            response = {
                                'role': 'assistant',
                                'content': message.get('content', ''),
                                'name': self.agent.name
                            }
                            if response['content']:
                                print(f"Using chat history response: {response['content'][:100]}...")
                                return response['content']
                            break
                
            print("\nNo valid response found in conversation")
            return "I apologize, but I couldn't process your request. Please try again with more details."
            
        except Exception as e:
            print(f"Detailed error in Simulation agent: {str(e)}")
            import traceback
            print(f"Stack trace: {traceback.format_exc()}")
            return f"I encountered an error while processing your request: {str(e)}"
    
    async def chat(self, message: str, history: List[Message]) -> str:
        """Process a chat message and return a response"""
        try:
            # Convert history to format expected by autogen
            formatted_history = [
                {"role": msg.role, "content": msg.content}
                for msg in history
            ]
            
            # Add current message - this should be 'user' since it's from the human
            formatted_history.append({"role": "user", "content": message})
            
            # Run AutoGen in a thread pool since it's not async
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                self._executor,
                self._generate_response_sync,
                formatted_history
            )
            
            return response
            
        except Exception as e:
            print(f"Error in Simulation agent chat: {str(e)}")
            return f"I encountered an error while processing your request: {str(e)}"
    
    async def setup_simulation(self, mesh_data: Dict[str, Any], physics_params: Dict[str, Any]) -> Dict[str, Any]:
        """Set up simulation case with mesh and physics parameters"""
        # TODO: Implement simulation setup logic
        return {
            "setup_complete": True,
            "physics_models": [],
            "boundary_conditions": {},
            "solver_settings": {}
        }
    
    async def run_simulation(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the simulation case"""
        # TODO: Implement simulation execution logic
        return {
            "simulation_complete": True,
            "iterations": 0,
            "residuals": {},
            "convergence_status": "converged"
        }
    
    async def analyze_results(self, results_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze simulation results and provide insights"""
        # TODO: Implement results analysis logic
        return {
            "analysis_complete": True,
            "key_metrics": {},
            "recommendations": [],
            "visualizations": []
        }
    
    async def validate_physics(self, physics_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate physics configuration"""
        # TODO: Implement physics validation logic
        return {
            "valid": True,
            "compatible_solvers": [],
            "warnings": [],
            "recommended_settings": {}
        } 