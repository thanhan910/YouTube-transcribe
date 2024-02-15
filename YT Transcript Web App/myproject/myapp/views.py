from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import whisper
from pytube import YouTube
import os
import re
import logging
import json

logging.basicConfig(level=logging.INFO)
model = whisper.load_model("base")


def extract_video_id(url_or_id):
    if "youtube.com" in url_or_id or "youtu.be" in url_or_id:
        # Extract the video ID from the URL
        if "v=" in url_or_id:
            return url_or_id.split("v=")[1].split("&")[0]
        elif "youtu.be" in url_or_id:
            return url_or_id.split("/")[-1]
    return url_or_id


def index(request):
    return render(request, 'index.html')


@csrf_exempt
def get_languages(request):
    if request.method == "POST":
        print([method for method in dir(request) if not method.startswith("_")])
        # Implement the logic similar to Flask's get_languages function
        data = json.loads(request.body)
        video_id = data["video_id"]
        video_id = extract_video_id(video_id)
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            languages = [
                {"code": transcript.language_code, "name": transcript.language}
                for transcript in transcript_list
            ]
            return JsonResponse({ 'languages' : languages })
        except Exception as e:
            return JsonResponse({'error' : str(e), 'status' : 500})
        

@csrf_exempt
def get_transcript(request):
    """
    Use OpenAI Whisper to transcribe the audio of a YouTube video.

    Credit: https://huggingface.co/spaces/SteveDigital/free-fast-youtube-url-video-to-text-using-openai-whisper
    """
    if request.method == "POST":
        data = json.loads(request.body)
        video_id = data["video_id"]
        video_id = extract_video_id(video_id)
        language = data["language"]
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
            return JsonResponse({'transcript' : transcript})
        except Exception as e:
            return JsonResponse({'error' : str(e), 'status' : 500})


@csrf_exempt
def get_video_text_whisper(request):
    """
    Use OpenAI Whisper to transcribe the audio of a YouTube video.

    Credit: https://huggingface.co/spaces/SteveDigital/free-fast-youtube-url-video-to-text-using-openai-whisper
    """
    if request.method == "POST":

        data = json.loads(request.body)
        video_id = data["video_id"]
        
        video_id = extract_video_id(video_id)
        
        if video_id == "":
            return JsonResponse({'error' : "Invalid video ID"}), 400
        
        url = f"https://www.youtube.com/watch?v={video_id}"

        yt_obj = YouTube(url)
        
        video = yt_obj.streams.filter(only_audio=True).first()

        # out_file = video.download(output_path="./local", filename_prefix="local-", filename="local-audio")
        # Remove local-audio.mp3
        filename = "local-audio.mp3"
        os.remove(filename) if os.path.exists(filename) else None
        out_file = video.download(output_path=".", filename=filename)
        logging.info(f"Downloaded audio file: {out_file}")
        if out_file is None:
            return JsonResponse({'error' : "Failed to download audio file"}), 400
        
        file_stats = os.stat(out_file)
        logging.info(f"Size of audio file in Bytes: {file_stats.st_size}")

        file_size_benchmark = 30_000_000

        if file_stats.st_size <= file_size_benchmark:
            base, ext = os.path.splitext(out_file)
            new_file = base + ".mp3"
            os.rename(out_file, new_file)
            a = new_file
            result = model.transcribe(a)
            os.remove(new_file) if os.path.exists(new_file) else None
            os.remove(out_file) if os.path.exists(out_file) else None
            return JsonResponse({'transcript' : result["text"].strip()})
        else:
            logging.error("File size is too large")
            os.remove(out_file) if os.path.exists(out_file) else None
            return JsonResponse({'error' : "File size is too large"}), 400



