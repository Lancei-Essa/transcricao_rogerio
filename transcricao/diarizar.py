import os
from pyannote.audio.pipelines import SpeakerDiarization
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def diarizar_audio(caminho_audio):
    """Aplica diarização no áudio extraído."""
    logger.debug("🔍 Iniciando diarização do áudio...")
    
    # Caminho para o modelo baixado previamente
    model_path = os.path.expanduser("~/.cache/torch/pyannote/models--pyannote--speaker-diarization/snapshots/0949b739131820b428f82569d616ba84a1903c11")
    
    # Criar pipeline sem acessar Hugging Face
    pipeline = SpeakerDiarization()
    pipeline.load_params(f"{model_path}/config.yaml")
    
    # Processar áudio
    diarization = pipeline(caminho_audio)
    
    # Criar lista de segmentos
    segmentos = []
    for i, (turn, _, speaker) in enumerate(diarization.itertracks(yield_label=True)):
        segmentos.append((turn.start, turn.end, speaker))
        logger.debug(f"🎙️ Segmento {i}: [{turn.start:.2f} - {turn.end:.2f}] {speaker}")
    
    return segmentos
