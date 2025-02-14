import os
from moviepy.editor import VideoFileClip
from config import AUDIO_DIR

def extract_audio(video_path, output_format="wav"):
    \"\"\"
    Extrai o áudio de um arquivo de vídeo e salva no formato desejado.

    :param video_path: Caminho do arquivo de vídeo
    :param output_format: Formato de saída (default: wav)
    :return: Caminho do arquivo de áudio extraído
    \"\"\"
    if not os.path.exists(AUDIO_DIR):
        os.makedirs(AUDIO_DIR)

    audio_path = os.path.join(AUDIO_DIR, os.path.basename(video_path).replace(".mp4", f".{output_format}"))

    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path, codec="pcm_s16le")

    return audio_path
