import os
from openai import OpenAI
from .prompts import SYSTEM_PROMPT_PREDICT

class FearForecast:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        self.model = 'gpt-4o'

    def _call_ai(self, prompt: str) -> str:
        if not self.api_key:
            return "This is a mock prediction. Please configure your OPENAI_API_KEY later to test actual AI functionality."
            
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=400,
            messages=[
                {'role': 'system', 'content': SYSTEM_PROMPT_PREDICT},
                {'role': 'user', 'content': prompt},
            ],
        )
        return response.choices[0].message.content

    def generate_forecast(self, fear: str, belief_strength: int) -> dict:
        prompt = f'Fear: {fear}\\nBelief strength: {belief_strength}%'
        response = self._call_ai(prompt)
        return {'fear': fear, 'belief_strength': belief_strength, 'ai_response': response}

    def generate_insight(self, fear: str, prediction: str, outcome: str) -> dict:
        prompt = (
            f'Original fear: {fear}\\n'
            f'AI prediction: {prediction}\\n'
            f'Actual outcome: {outcome}'
        )
        response = self._call_ai(prompt)
        return {'outcome': outcome, 'insight': response}

