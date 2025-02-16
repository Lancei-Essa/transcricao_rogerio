import os
import subprocess

def extrair_audio(caminho_video):
    """Extrai o áudio do vídeo e salva como WAV."""
    caminho_base = os.path.splitext(caminho_video)[0]  # Remove extensão do vídeo
    caminho_audio = f"{caminho_base}.wav"

    comando = [
        "ffmpeg", "-i", caminho_video, "-q:a", "0", "-map", "a",
        "-ac", "1", "-ar", "16000", "-y", caminho_audio  # Formato WAV mono, 16kHz
    ]
    
    try:
        subprocess.run(comando, check=True)
        return caminho_audio
    except subprocess.CalledProcessError as e:
        print(f"Erro ao extrair áudio: {e}")
        return None
