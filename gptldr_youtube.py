import speech_recognition as sr
from pydub import AudioSegment
from pytube import YouTube, extract
from youtube_transcript_api import YouTubeTranscriptApi, _errors
from pathlib import Path
from transcriptor import get_transcript

import sys
import path
directory = path.Path(__file__).abspath()
sys.path.append(directory.parent.parent)
import GPTLDRCore.gptldr_core as gptldr_core

# temporary patch for buggy pytube==15.0.0 see" https://github.com/pytube/pytube/issues/1678
import pytube.cipher
pytube.cipher.get_transform_object = lambda a,b: []

# With subs
# Midjourney AI: Text To Image Supercharged!
# https://www.youtube.com/watch?v=jbe6t4GiljU

# No subs
# Huge fire at crimea military site sparks evacuations | DW News
# https://www.youtube.com/watch?v=LiJ4-I4RTII


def extract_title(video_streams):
    return video_streams[0].title



def transcript_captions(url):    
    
    srt = None

    try:
        # assigning srt variable with the list
        # of dictionaries obtained by the get_transcript() function
        srt = YouTubeTranscriptApi.get_transcript(extract.video_id(url))
            
    # catch errors.
    except _errors.TranscriptsDisabled as e:
        # print("No subtitles availiable for this video")
        pass

    return srt


def get_video_streams(video_url):
    video = YouTube(video_url)
    return video.streams


def download_video(video_streams, filename):
    # audio = video.streams.filter(only_audio = True).first()
    video = video_streams.get_highest_resolution()

    try:
        video.download(filename=filename)
        pass
    except:
        print("Failed to download audio")


def extract_wav(vid_filename, wav_filename):
    # Load the video file
    video = AudioSegment.from_file(vid_filename, format="mp4")
    audio = video.set_channels(1).set_frame_rate(16000).set_sample_width(2)
    audio.export(wav_filename, format="wav")


def read_transcript(txt_filename):
    data = ""
    with open(txt_filename, 'r') as file:
        data = file.read().replace('\n', '')
    return data


def extract_title_text(url):
    tmp_dir = "out"
    vid_filename = f"{tmp_dir}/" + "tmp_yt_video.mp4"
    wav_filename = f"{tmp_dir}/" + "tmp_yt_audio.wav"
    txt_filename = f"{tmp_dir}/" + "yt_tldr.txt"
    
    Path(tmp_dir).mkdir(parents=True, exist_ok=True)

    video_streams = get_video_streams(url)

    title = extract_title(video_streams)
    text = ""

    if not (text := transcript_captions(url)):
        download_video(video_streams, vid_filename)
        extract_wav(vid_filename, wav_filename)
        text = get_transcript(wav_filename, txt_filename, tmp_dir)

    return title, text


def run(url):
    title, text = extract_title_text(url)
    gptldr_core.run(title, text)