import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt

class Summary(APIView):
    def __init__(self):
        load_dotenv('../../.env')
        self.api_key = 'b34ffbe1b154480ebe518c68c6031887'
        self.endpoint = 'https://sunhackathon35.openai.azure.com/'
    
    def create_ai_client(self):
        return AzureOpenAI(
            api_key=self.api_key,
            api_version="2023-05-15",
            azure_endpoint=self.endpoint,
        )
    
    def post(self, request):
        text = request.POST.get('text_input')
        response_data = self.summarize(text)
        return response_data
    
    
    def summarize(self, text):
        text_input = text
        client = self.create_ai_client()

        system_prompt = 'Create a summary of the following text.'
        prompt = text_input

        print('Starting summarizing ...', end = '')
        response = client.chat.completions.create(
            model = 'GPT35TURBO16K',
            messages=[{'role':'system','content': system_prompt},
                        {'role':'user','content': prompt}],
            max_tokens=1024,
            temperature=1,
            top_p=1
        )
        print('Done')
        r = response.choices[0].message.content
        return Response(r)