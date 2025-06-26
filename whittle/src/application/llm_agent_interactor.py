import anthropic
import openai
from whittle.src.entities.llm_agent import LLMAgent
from typing import List, Dict
import os
from dotenv import load_dotenv

class OpenAILLMAgent(LLMAgent):
    def __init__(self, system_prompt: str):
        super().__init__(system_prompt=system_prompt)
        self.client = openai.Client(api_key=self._get_api_key_from_env())
        self.messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]

    def return_response(self, prompt: str) -> str:
        self.messages.append({"role": "user", "content": prompt})
        response = self.client.chat.completions.create(
            model="gpt-4.1",
            messages=self.messages,
            temperature=0.7,
            stream=True
        )
        # ai_response = response.choices[0].message.content
        # self.messages.append({"role": "assistant", "content": ai_response})
        # return ai_response
        self.messages.append({"role": "assistant", "content": response})
        return response
    
    def return_response_with_tools(self, prompt: str, tools: list[str]) -> str:
        self.messages.append({"role": "user", "content": prompt})
        response = self.client.chat.completions.create(
            model="gpt-4.1",
            messages=self.messages,
            temperature=0.7,
            stream=False,
            tools=tools
        )
        ai_response = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": ai_response})
        return ai_response

    def _store_conversation(self, conversation: list[str]) -> None:
        self.messages.extend(conversation)

    def _get_api_key_from_env(self) -> str:
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        return api_key


class ClaudeLLMAgent(LLMAgent):
    def __init__(self, system_prompt: str):
        super().__init__(system_prompt=system_prompt)
        self.client = anthropic.Anthropic(api_key=self._get_api_key_from_env())
        self.messages: List[Dict[str, str]] = [{"role": "user", "content": system_prompt}]

    def return_response(self, prompt: str) -> str:
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            messages=[{"role": "user", "content": prompt}],  # Only send the current prompt
            temperature=0.7,
            max_tokens=8192,
            stream=False
        )
        ai_response = response.content[0].text
        self.messages.append({"role": "assistant", "content": ai_response})
        return response
    
    def return_response_with_tools(self, prompt: str, tools: list[str]) -> str:
        self.messages.append({"role": "user", "content": prompt})
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            messages=self.messages,
            temperature=0.7,
            max_tokens=8192,
            stream=False,
            tools=tools
        )
        # Don't store the response in conversation history for tool calls
        # This prevents the model from repeating itself after tool results
        return response

    def _store_conversation(self, conversation: list[str]) -> None:
        self.messages.extend(conversation)

    def _get_api_key_from_env(self) -> str:
        load_dotenv()
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        return api_key