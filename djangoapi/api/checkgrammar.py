import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt

class CheckGRM(APIView):
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
        text = text[0].upper() + text[1:]
        response_data = self.check_grm(text)
        return response_data

    def find_dif(self, incorrect, fixed):
        incorrect_word_list = []
        fixed_word_list = []

        for incorrect_sentence, fixed_sentence in zip(incorrect, fixed):
            # Loại bỏ dấu chấm cuối câu
            if fixed_sentence.endswith('.'):
                fixed_sentence = fixed_sentence[:-1]
            if incorrect_sentence.endswith('.'):
                incorrect_sentence = incorrect_sentence[:-1]

            # Tìm các từ khác nhau giữa incorrect_sentence và fixed_sentence
            incorrect_words = set(incorrect_sentence.split())
            fixed_words = set(fixed_sentence.split())
            different_words = incorrect_words.symmetric_difference(fixed_words)
            correct_words = fixed_words.symmetric_difference(incorrect_words)

            # Thêm từ sai của list incorrect vào danh sách incorrect_word
            incorrect_word_list.extend([word for word in different_words if word in incorrect_words])

            if not incorrect_word_list:
                additional_words = [word for word in fixed_words if word not in incorrect_words]
                fixed_word_list.extend(additional_words)
            else:
            # Thêm từ đã sửa của list fixed vào danh sách fixed_word
                fixed_word_list.extend([word for word in correct_words if word in fixed_words])

        return incorrect_word_list, fixed_word_list
    
    def fixes(self,text):
        client = self.create_ai_client()
        system_prompt = 'You will receive a sentence. Your task is to correct grammar errors in accordance with English standards.'
        prompt = text

        print('Fixing ...', end='')
        response = client.chat.completions.create(
            model='GPT35TURBO',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt}
            ],
            max_tokens=1024,
            temperature=1,
            top_p=1
        )
        print('Done')
        return response.choices[0].message.content.strip()
    

    def check_grm(self, text):
        text_input = text
        client = self.create_ai_client()
        
        system_prompt = 'You will be given a paragraph or a sentence. Your task is to check standard English grammar. If the paragraph has no errors, the returned result is that paragraph.'
        prompt = text_input

        response = client.chat.completions.create(
            model='GPT35TURBO',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt}
            ],
            max_tokens=1024,
            temperature=1,
            top_p=1
        )
        print('Done')

        # Extracting the corrected text from the response
        corrected_text = response.choices[0].message.content.strip()

        # Tách câu đã sửa thành từng câu
        corrected_sentences = [sentence.strip() for sentence in corrected_text.split('.') if sentence.strip()]
    
        # Tách câu gốc thành từng câu
        original_sentences = [sentence.strip() for sentence in text_input.split('.') if sentence.strip()]

        # Danh sách câu đã phát hiện sai ngữ pháp
        incorrect_sentences = []

        # Danh sách câu đã sửa lỗi
        fixed_sentences_list = []

        # Danh sách câu đúng ngữ pháp
        correct_sentences_list = []

        # Danh sách các lỗi ngữ pháp
        incorrect_word_list = []

        # Danh sách các lỗi đã sửa
        fixed_word_list = []

        # So sánh từng câu
        for original_sentence, corrected_sentence in zip(original_sentences, corrected_sentences):
            if original_sentence != corrected_sentence:
                # Câu đã phát hiện sai ngữ pháp
                incorrect_sentences.append(original_sentence)
                # Sửa lỗi ngữ pháp và thêm vào danh sách câu đã sửa
                fixed_sentence = self.fixes(original_sentence)
                fixed_sentences_list.append(fixed_sentence)
                incorrect_word_list, fixed_word_list = self.find_dif(incorrect_sentences, fixed_sentences_list)

            else:
            # Câu đúng ngữ pháp, thêm vào danh sách câu đúng
                correct_sentences_list.append(original_sentence)

        result = {
            'original_text': text_input,
            'corrected_text': corrected_text,
            'incorrect_sentences': incorrect_sentences,
            'fixed_sentences': fixed_sentences_list,
            'incorrect_word': incorrect_word_list,
            'fixed_word': fixed_word_list,
            'correct_sentences': correct_sentences_list
        }
        return Response(result)
    

    