import yt_dlp

def download_audios(videoIds, save_to_folder = 'audio', file_format='wav'):
    '''Download audio files from YouTube videos'''

    URLS = [f'https://www.youtube.com/watch?v={videoId}' for videoId in videoIds]

    ydl_opts = {
        'format': f'{file_format}/bestaudio/best',
        'outtmpl': f'{save_to_folder}/%(id)s.%(ext)s', # use 'outtmpl': 'output/%(title)s.%(ext)s' if you want the filename to be the title of the video
        'postprocessors': [{  # Extract audio using ffmpeg
            'key': 'FFmpegExtractAudio',
            'preferredcodec': file_format,
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download(URLS)



