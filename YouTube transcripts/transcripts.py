from pytube import YouTube
from pytube import Channel
from youtube_transcript_api import YouTubeTranscriptApi
import spacy
import os

def reformat_folder_name(s: str):
    '''Remove those invalid characters so that the string is a valid folder name.'''
    invalid_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
    for char in invalid_chars:
        s = s.replace(char, '')
    return s


def dowload_transcript_by_id(videoId: str, folder_path):
    '''Download the transcript of the video with the given videoId and save it to the given folder_path.'''

    try:
        data = YouTubeTranscriptApi.get_transcript(videoId)
    except:
        try:
            data = YouTubeTranscriptApi.get_transcript(videoId, languages=['en', 'en-US', 'en-GB', 'en-CA', 'en-AU', 'en-IE', 'en-ZA', 'en-IN', 'vi', 'vi-VN'])
        except:
            return False
    
    lines = list(map(lambda x: x['text'], data))

    # create the folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Save raw transcript with separated lines
    with open(os.path.join(folder_path, '1.original.txt'), 'w', encoding='utf8') as f:
        f.write('\n'.join(lines))

    # Combine lines into sentences by finding end-of-sentence characters. 
    new_lines = []
    current_line = ''
    for x in data:
        line = x['text'].replace('\n', ' ').strip()
        if line.isdigit() or line == '':
            new_lines.append(line)
        else:
            current_line += ' ' + line
            if current_line[-1] in ['.', '?', '!', ':']:
                new_lines.append(current_line.strip())
                current_line = ''
    with open(os.path.join(folder_path, '2.combined.txt'), 'w', encoding='utf8') as f:
        f.write('\n'.join(new_lines))


    # Use spacey to recognize sentences and combine separated lines into sentences.

    # Load the English language model in Spacy
    nlp = spacy.load('en_core_web_sm')

    # Merge the lines into a single string
    text = ' '.join(lines)

    # Process the text with Spacy
    doc = nlp(text)

    # Retrieve the sentences
    sentences = [sent.text for sent in doc.sents]

    # Save the sentences
    with open(os.path.join(folder_path, '3.spacey combine.txt'), 'w', encoding='utf8') as f:
        f.write('\n'.join(sentences))

    # Initialize a list to store the output lines
    output_lines = []

    # Loop through the sentences in the text
    for sent in doc.sents:
        # If the sentence contains more than 15 words, split it into multiple lines
        if len(sent) > 15:
            # Split the sentence into chunks of 15 words
            chunks = [sent[i:i+15] for i in range(0, len(sent), 15)]

            # Join the chunks into lines and add them to the output
            for chunk in chunks:
                output_lines.append(chunk.text)
        else:
            # If the sentence is not too long, add it to the output as-is
            output_lines.append(sent.text)

    # Join the output lines into a single string and return it
    # Save the sentences
    with open(os.path.join(folder_path, '4.spacey split.txt'), 'w', encoding='utf8') as f:
        f.write('\n'.join(output_lines))

    return True


def download_transcripts(videoIds: list, main_folder = 'transcripts'):
    '''Download and save transcripts of videos with the given videoIds.'''

    # create the folder if it doesn't exist
    if not os.path.exists(main_folder):
        os.makedirs(main_folder)

    download_failed = []

    for videoId in videoIds:

        # Join the main folder with the videoId to create a new folder path
        folder_path = os.path.join(main_folder, videoId)

        download_success = dowload_transcript_by_id(videoId, folder_path)

        if(not download_success):
            print(f'Cannot get transcript for video: {videoId}')
            download_failed.append(videoId)


def download_channel_all_videos_transcripts(channel_url):
    '''Save transcripts of all videos in the given channel.'''

    channel = Channel(channel_url)
    # Define the main folder to save the transcripts
    main_folder = reformat_folder_name(channel.channel_name)

    # create the folder if it doesn't exist
    if not os.path.exists(main_folder):
        os.makedirs(main_folder)

    download_failed = []

    for video in channel.videos:

        # Join the main folder with the videoId to create a new folder path
        folder_name = reformat_folder_name(f"{video.publish_date.strftime('%Y%m%d')} - {video.title} - {video.video_id}")
        folder_path = os.path.join(main_folder, folder_name)

        # Download the transcript
        download_success = dowload_transcript_by_id(video.video_id, folder_path)

        if(not download_success):
            print(f'Cannot get transcript for video: {video.watch_url} - {video.title}')
            download_failed.append(video.video_id)

if __name__ == "__main__":
    channel_url = ""  # Replace with the channel URL
    download_channel_all_videos_transcripts(channel_url)
    videoIds = [] # Add more video URLs here
    download_transcripts(videoIds=videoIds)


