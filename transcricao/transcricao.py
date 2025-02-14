import os
import whisper
from config import AUDIO_DIR, TRANSCRICOES_DIR

def transcrever_audio(audio_path):
    \"\"\"
    Transcreve um arquivo de áudio usando o modelo Whisper.

    :param audio_path: Caminho do arquivo de áudio
    :return: Texto transcrito
    \"\"\"
    if not os.path.exists(TRANSCRICOES_DIR):
        os.makedirs(TRANSCRICOES_DIR)

    # Carregar o modelo Whisper localmente
    model = whisper.load_model("large-v2", download_root=os.path.join(os.path.dirname(__file__), "../modelos/whisper-large-v2"))

    # Carregar o áudio e transcrever
    result = model.transcribe(audio_path)

    # Salvar a transcrição em um arquivo
    transcricao_path = os.path.join(TRANSCRICOES_DIR, os.path.basename(audio_path).replace(".wav", "_transcricao.txt"))
    with open(transcricao_path, "w", encoding="utf-8") as f:
        f.write(result["text"])

    return transcricao_path
