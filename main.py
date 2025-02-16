from transcricao.selecionar_arquivo import selecionar_arquivo
from transcricao.extrair_audio import extrair_audio
from transcricao.transcrever import transcrever_audio
from transcricao.salvar_transcricao import salvar_transcricao
import os

def main():
    # 1️⃣ Seleciona o vídeo
    caminho_video = selecionar_arquivo()
    if not caminho_video:
        print("Nenhum arquivo selecionado.")
        return

    # 2️⃣ Extrai o áudio
    caminho_audio = extrair_audio(caminho_video)
    if not caminho_audio:
        print("Erro ao extrair o áudio.")
        return

    # 3️⃣ Transcreve o áudio
    print("Transcrevendo... Isso pode levar alguns minutos.")
    texto_transcricao = transcrever_audio(caminho_audio)

    # 4️⃣ Salva a transcrição
    salvar_transcricao(caminho_audio, texto_transcricao)

    # 5️⃣ Remove o áudio temporário
    os.remove(caminho_audio)
    print("Áudio temporário removido.")

if __name__ == "__main__":
    main()
