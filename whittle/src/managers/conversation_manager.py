from typing import List, Dict
from whittle.src.interfaces.conversation_interface import IAIConversationManager
import openai

class OpenAIConversationManager(IAIConversationManager):
    def __init__(self, api_key: str, system_prompt: str):
        self.client = openai.Client(api_key=api_key)
        self.messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]
    
    def get_response(self, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=self.messages,
            temperature=0.7,
        )
        
        ai_response = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": ai_response})
        return ai_response