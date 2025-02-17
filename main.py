import os
from pyannote.audio.pipelines import SpeakerDiarization
from transcricao.selecionar_arquivo import selecionar_arquivo
from transcricao.extrair_audio import extrair_audio
from transcricao.transcrever import transcrever_audio
from transcricao.salvar_transcricao import salvar_transcricao
from transcricao.diarizar import diarizar_audio

def main():
    """Fluxo principal do programa."""
    caminho_video = selecionar_arquivo()
    if not caminho_video:
        print("Nenhum arquivo selecionado.")
        return

    caminho_audio = extrair_audio(caminho_video)
    if not caminho_audio:
        print("Erro ao extrair o áudio.")
        return

    print("🔍 Aplicando diarização...")
    segmentos = diarizar_audio(caminho_audio)

    print("🎙️ Transcrevendo o áudio...")
    texto_transcricao = transcrever_audio(caminho_audio)

    print("📝 Formatando a transcrição...")
    transcricao_formatada = ""
    for inicio, fim, speaker in segmentos:
        trecho = f"[{inicio:.2f} - {fim:.2f}] {speaker}: {texto_transcricao}\n"
        transcricao_formatada += trecho

    salvar_transcricao(caminho_audio, transcricao_formatada)

    print("✅ Transcrição completa!")
    os.remove(caminho_audio)

if __name__ == "__main__":
    main()
