import httpx
import os
import whisper
import re
import pysrt
import datetime
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.http import FileResponse
from django.http import HttpResponse
from tempfile import NamedTemporaryFile
from ..service.translateOpenAI import OpenAIService

class Subtitle(APIView):
    @csrf_exempt
    def post(self, request):
        path = request.POST.get('path_video')
        response_data = self.process_subtitle_request(path)
        return self.format_response(response_data)

    def process_subtitle_request(self, video_path):
        video_content = self.download_video(video_path)

        if video_content:
            mp3_file_path = self.get_safe_filename(video_path.replace('.mp4', '.mp3'))
            with open(mp3_file_path, 'wb') as mp3_file:
                mp3_file.write(video_content)

            result = self.speech_to_text(mp3_file_path)

            # Xóa file MP3 sau khi sử dụng (nếu cần)
            os.remove(mp3_file_path)

            vtt_content = self.convert_format_vtt(result)

            # Tạo file .vtt tạm thời
            with NamedTemporaryFile(mode='w+', suffix='.vtt', delete=False) as vtt_file:
                vtt_file.write(self.convert_to_vtt(vtt_content))
            
            response = {
                'success': True,
                'subtitle_file': open(vtt_file.name, 'rb'),
                'filename': 'subtitle.vtt'
            }
        else:
            response = {'error': 'Failed to download video'}

        return response

    def format_response(self, response_data):
        if response_data.get('success'):
            subtitle_file = response_data['subtitle_file']
            filename = response_data['filename']

            response = FileResponse(subtitle_file)
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
        else:
            response = Response(response_data)

        return response

    def download_video(self, url):
        with httpx.Client() as client:
            response = client.get(url, timeout=60)
            if response.status_code == 200:
                return response.content
            else:
                # Xử lý lỗi nếu cần
                return None

    def speech_to_text(self, file_path):
        # Đảm bảo `ffmpeg` có trong biến môi trường PATH
        os.environ["PATH"] += os.pathsep + "C:\\ffmpeg-master-latest-win64-gpl-shared\\bin"

        model = whisper.load_model("medium")
        result = model.transcribe(file_path, language='en')
        return result

    def get_safe_filename(self, filename):
        # Xóa tất cả các ký tự không hợp lệ cho tên file
        safe_filename = re.sub(r'[^\w\s.-]', '', filename)
        return safe_filename
    
    def convert_format_vtt(self, data):
        subs = [
            pysrt.SubRipItem(
                index=i + 1,
                start=pysrt.SubRipTime(seconds=segment["start"]),
                end=pysrt.SubRipTime(seconds=segment["end"]),
                text=segment["text"]
            )
            for i, segment in enumerate(data["segments"])
        ]
        return pysrt.SubRipFile(items=subs)
    
    def convert_to_vtt(self, subs):
        vtt_content = "WEBVTT\n\n"
        for sub in subs:
            # Chuyển đổi giá trị thời gian sang số nguyên
            start_time = int(sub.start.seconds * 1000) + sub.start.milliseconds
            end_time = int(sub.end.seconds * 1000) + sub.end.milliseconds
            vtt_content += f"{self.format_time(start_time)} --> {self.format_time(end_time)}\n{sub.text}\n\n"
        return vtt_content

    def format_time(self, milliseconds):
        # Chuyển đổi giá trị thời gian từ milliseconds sang định dạng HH:MM:SS.SSS
        return str(datetime.timedelta(milliseconds=milliseconds))


class Translate(APIView):
    @csrf_exempt
    def post(self, request):
        language = request.POST.get('lang')
        webvtt_content = request.POST.get('webvtt')

        translate_service = OpenAIService()
        translated_content = translate_service.translate(webvtt_content, language, language)

        response = HttpResponse(translated_content, content_type='text/vtt')
        response['Content-Disposition'] = 'attachment; filename="translated_subtitle.vtt"'
        
        return response