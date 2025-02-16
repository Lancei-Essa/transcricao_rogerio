import os

def salvar_transcricao(caminho_audio, texto_transcricao):
    """Salva a transcrição em um arquivo de texto."""
    caminho_base = os.path.splitext(caminho_audio)[0]  # Remove extensão .wav
    caminho_txt = f"{caminho_base}.txt"

    with open(caminho_txt, "w", encoding="utf-8") as arquivo:
        arquivo.write(texto_transcricao)
    
    print(f"Transcrição salva em: {caminho_txt}")
