import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()
class OpenAIService:
    def __init__(self):
        self.api_key = os.getenv('AZURE_OPENAI_KEY')
        self.endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')

    def create_ai_client(self):
        return AzureOpenAI(
            api_key=self.api_key,
            api_version="2023-05-15",
            azure_endpoint=self.endpoint,
        )

    def translate(self, result, role, language):
        client = self.create_ai_client()
        system_prompt = f'I want you to be a {language} human and translate my text from english to {language} and keeping format file vtt'
        prompt = result
        
        response = client.chat.completions.create(
            model='GPT35TURBO16K',
            messages=[{'role': 'system', 'content': system_prompt},
                      {'role': 'user', 'content': prompt}],
            max_tokens=2048,
            temperature=1
        )
        return response.choices[0].message.content
