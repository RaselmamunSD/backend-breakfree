import os
from openai import OpenAI
from .prompts import SYSTEM_PROMPT_CHAT

class AICoach:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        self.model = 'gpt-4o'

    def get_reply(self, messages_list) -> str:
        if not self.api_key:
            return "This is a mock response. Please add OPENAI_API_KEY in your environment to connect to actual AI."
        
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=400,
            messages=messages_list,
        )
        return response.choices[0].message.content

