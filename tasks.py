from pydub import AudioSegment
import time
import logging
import os
from invoke import task
from transcricao.transcricao import transcrever_audio, validar_token

logger = logging.getLogger(__name__)

def dividir_audio(audio_path, segment_duration=30000):
    """
    Divide o arquivo de áudio em segmentos menores e salva como arquivos temporários.

    :param audio_path: Caminho para o arquivo de áudio.
    :param segment_duration: Duração de cada segmento em milissegundos (30s padrão).
    :return: Lista de caminhos para arquivos segmentados.
    """
    audio = AudioSegment.from_file(audio_path)
    segmentos = []
    for i in range(0, len(audio), segment_duration):
        segmento = audio[i:i+segment_duration]
        segment_path = f"{audio_path}_segment_{i//segment_duration}.wav"
        segmento.export(segment_path, format="wav")
        segmentos.append(segment_path)
    return segmentos

@task(help={
    "file": "Caminho para o arquivo de áudio (formato .wav).",
    "token": "Token de autenticação do Hugging Face."
})
def process_audio(ctx, file, token):
    """
    Realiza a transcrição de um arquivo de áudio usando Whisper e PyAnnote.
    """
    if not validar_token(token):
        print("Token inválido ou não autorizado.")
        return

    start_time = time.time()
    logger.info("Iniciando transcrição...")

    try:
        transcricao = transcrever_audio(file, token)
        output_path = file.replace(".wav", "_transcricao.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            for item in transcricao:
                linha = f"[{item['start']:.2f} - {item['end']:.2f}] {item['speaker']}: {item['text']}\n"
                f.write(linha)
        print(f"Transcrição salva com sucesso no arquivo: {output_path}")
    except Exception as e:
        print(f"Erro ao transcrever o áudio: {e}")

    elapsed_time = time.time() - start_time
    logger.info(f"Transcrição concluída em {elapsed_time:.2f} segundos.")

def limpar_segmentos(segmentos):
    for segmento in segmentos:
        os.remove(segmento)
    logger.info("Arquivos temporários removidos com sucesso.")
