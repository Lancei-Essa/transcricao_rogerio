import os
import subprocess

# Forçar as bibliotecas a operarem em modo offline
os.environ['HF_HUB_OFFLINE'] = '1'

from transcricao.selecionar_arquivo import selecionar_arquivo
from transcricao.extrair_audio import extrair_audio
from transcricao.transcrever import transcrever_audio
from transcricao.salvar_transcricao import salvar_transcricao
from transcricao.diarizar import diarizar_audio
from transcricao.sincronizar_transcricao import sincronizar_diarizacao_com_transcricao

def extrair_audio(video_path):
    """Extrai o áudio do vídeo usando ffmpeg."""
    audio_path = os.path.splitext(video_path)[0] + ".wav"
    subprocess.run(["ffmpeg", "-i", video_path, "-q:a", "0", "-map", "0:a:0", "-ac", "1", "-ar", "16000", "-y", audio_path])
    return audio_path

def main():
    """Fluxo principal do programa."""
    caminho_video = selecionar_arquivo()
    if not caminho_video:
        print("❌ Nenhum arquivo selecionado.")
        return

    caminho_audio = extrair_audio(caminho_video)
    if not caminho_audio:
        print("❌ Erro ao extrair o áudio.")
        return

    print("🔍 Aplicando diarização...")
    segmentos_diarizacao = diarizar_audio(caminho_audio)

    print("🎙️ Transcrevendo o áudio...")
    resultado = transcrever_audio(caminho_audio)

    if isinstance(resultado, tuple) and len(resultado) == 2:
        caminho_transcricao, texto_transcricao = resultado
    else:
        print("❌ Erro: `transcrever_audio` retornou um valor inesperado:", resultado)
        return

    if not texto_transcricao:
        print("❌ Erro na transcrição. O texto retornado está vazio.")
        return

    # Inspecionar o formato da variável texto_transcricao
    print(f"Texto transcrito (tipo): {type(texto_transcricao)}")
    print(f"Primeiros elementos: {texto_transcricao[:5]}")  # Mostra os primeiros elementos

    print("📝 Formatando a transcrição...")
    transcricao_formatada = sincronizar_diarizacao_com_transcricao(segmentos_diarizacao, texto_transcricao)

    print("💾 Salvando transcrição formatada...")
    salvar_transcricao(caminho_audio, transcricao_formatada)

    print("✅ Transcrição completa!")
    os.remove(caminho_audio)

if __name__ == "__main__":
    main()
