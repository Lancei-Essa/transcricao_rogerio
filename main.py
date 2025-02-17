import os
import torch
from pyannote.audio.pipelines import SpeakerDiarization
from pyannote.core import Segment
from transcricao import transcrever_audio
from transcricao.selecionar_arquivo import selecionar_arquivo
from transcricao.extrair_audio import extrair_audio
from transcricao.salvar_transcricao import salvar_transcricao
from transcricao.transcrever import transcrever_audio


def diarizar_audio(caminho_audio):
    """Aplica diarização no áudio extraído."""
    print("🔍 Aplicando diarização...")
    
    # Caminho para o modelo baixado previamente
    model_path = os.path.expanduser("~/.cache/torch/pyannote/models--pyannote--speaker-diarization/snapshots/0949b739131820b428f82569d616ba84a1903c11")
    
    # Criar pipeline sem acessar Hugging Face
    pipeline = SpeakerDiarization()
    pipeline.load_params(f"{model_path}/config.yaml")
    
    # Processar áudio
    diarization = pipeline(caminho_audio)
    
    # Criar lista de segmentos
    segmentos = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        segmentos.append((turn.start, turn.end, speaker))
    
    return segmentos

def main():
    """Fluxo principal do programa."""
    caminho_video = selecionar_arquivo()
    caminho_audio = extrair_audio(caminho_video)
    
    # Aplicar diarização para identificar os falantes
    segmentos = diarizar_audio(caminho_audio)
    
    # Transcrever áudio
    texto_transcricao = transcrever_audio(caminho_audio)
    
    # Criar transcrição formatada com falantes identificados
    transcricao_formatada = ""
    for inicio, fim, speaker in segmentos:
        trecho = f"[{inicio:.2f} - {fim:.2f}] {speaker}: {texto_transcricao}\n"
        transcricao_formatada += trecho
    
    # Salvar transcrição formatada
    caminho_txt = salvar_transcricao(caminho_audio, transcricao_formatada)
    
    print(f"✅ Transcrição completa! Arquivo salvo em: {caminho_txt}")
    
    # Remover arquivo de áudio temporário
    os.remove(caminho_audio)

if __name__ == "__main__":
    main()
