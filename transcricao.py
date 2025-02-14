from logs.logger import logger
import whisper
import os
import logging
import requests
from transformers import pipeline
import argparse
from multiprocessing import Pool
from pydub import AudioSegment
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

def validar_token(token):
    url = "https://huggingface.co/api/whoami"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        logger.info("Token do Hugging Face validado com sucesso.")
        return True
    else:
        logger.error("Token do Hugging Face inválido ou não autorizado.")
        return False

def validar_pacotes_python():
    pacotes = ["whisper", "torch", "transformers", "pytest", "requests", "PySide6"]
    for pacote in pacotes:
        try:
            __import__(pacote)
            logger.info(f"Pacote {pacote} validado com sucesso.")
        except ImportError:
            logger.error(f"Erro: O pacote {pacote} não está instalado corretamente.")
            raise

def dividir_audio(audio_path, segment_duration=30000):
    """
    Divide o arquivo de áudio em segmentos menores.

    :param audio_path: Caminho do arquivo de áudio.
    :param segment_duration: Duração de cada segmento em milissegundos (padrão: 30 segundos).
    :return: Lista de segmentos.
    """
    audio = AudioSegment.from_file(audio_path)
    segmentos = [audio[i:i+segment_duration] for i in range(0, len(audio), segment_duration)]
    return segmentos

def transcrever_segmento(segmento):
    try:
        segmento.export("temp.wav", format="wav")
        modelo = whisper.load_model("large")
        resultado = modelo.transcribe("temp.wav", language="pt")

        logger.debug(f"Segmentos extraídos do Whisper: {resultado.get('segments', [])}")

        return [
            {
                "start": seg.get("start", 0), 
                "end": seg.get("end", 0), 
                "text": seg.get("text", "")
            } 
            for seg in resultado.get("segments", []) 
            if isinstance(seg, dict) and "start" in seg and "end" in seg
        ]
    except Exception as e:
        logger.error(f"Erro ao processar segmento: {e}")
        return []

def transcrever_audio(audio_path):
    """
    Transcreve um arquivo de áudio para texto usando o Whisper.

    :param audio_path: Caminho para o arquivo de áudio (.wav)
    :return: Lista de dicionários com 'start', 'end', 'text'
    """
    if not audio_path.lower().endswith(".wav"):
        logger.error("Apenas arquivos .wav são suportados.")
        raise ValueError("Formato de arquivo inválido. Apenas arquivos .wav são suportados.")
    
    try:
        # Dividir o áudio em segmentos
        segmentos = dividir_audio(audio_path)
    except Exception as e:
        logger.error(f"Erro durante a divisão do áudio: {e}")
        raise

    try:
        with Pool() as pool:
            resultados = pool.map(transcrever_segmento, segmentos)
        resultados_planos = [seg for lista in resultados for seg in lista]
    except Exception as e:
        logger.error(f"Erro durante a transcrição com Whisper: {e}")
        raise

    if not resultados_planos:
        logger.error("Nenhum segmento retornado pelo Whisper.")
        raise ValueError("Nenhuma transcrição encontrada.")

    # Registrar os dados antes de combinar
    logger.debug(f"🔎 Dados antes de combinar: {resultados_planos}")

    try:
        return combinar_resultados(resultados_planos)
    except Exception as e:
        logger.error(f"🚨 Erro ao combinar resultados: {e}", exc_info=True)
        raise

def combinar_resultados(transcricao_whisper):
    logger.debug(f"Dados recebidos para combinar: {transcricao_whisper}")

    if not transcricao_whisper:
        logger.warning("Nenhum segmento retornado pelo Whisper.")
        return []

    logger.info("Combinando resultados de transcrição...")
    combined_results = []

    try:
        for i, segmento in enumerate(transcricao_whisper):
            logger.debug(f"Processando segmento {i}: {segmento} (Tipo: {type(segmento)})")  # Adicionando log de depuração

            if not isinstance(segmento, dict):
                logger.error(f"Segmento inesperado ignorado: {segmento}")
                continue  # Pular segmentos inválidos

            # Garantir que os atributos existam antes de acessar
            start_time = segmento.get('start')
            end_time = segmento.get('end')
            text = segmento.get('text', "")

            if start_time is None or end_time is None:
                logger.error(f"Segmento malformado detectado e será ignorado: {segmento}")
                continue  # Pular segmentos inválidos

            combined_results.append(
                {
                    "start": start_time,
                    "end": end_time,
                    "text": text
                }
            )

        if not combined_results:
            logger.warning("Nenhum resultado combinado gerado. Verifique os segmentos retornados.")
            return []

        logger.info("Resultados combinados com sucesso.")
        return combined_results
    except Exception as e:
        logger.error(f"Erro ao combinar resultados: {e}")
        raise

def transcrever_whisper(arquivo_audio, idioma='pt'):
    """
    Transcreve um arquivo de áudio para texto usando o Whisper.

    :param arquivo_audio: Caminho do arquivo de áudio (.wav)
    :param idioma: Idioma do áudio, padrão é 'pt' (português)
    :return: Lista de segmentos transcritos
    """
    logger.info(f"Iniciando transcrição do arquivo: {arquivo_audio} com idioma '{idioma}'")

    if not os.path.exists(arquivo_audio):
        logger.error(f"Arquivo de áudio não encontrado: {arquivo_audio}")
        raise FileNotFoundError(f"Arquivo de áudio não encontrado: {arquivo_audio}")

    logger.info(f"Carregando modelo Whisper")
    try:
        modelo = whisper.load_model("large")
        resultado = modelo.transcribe(arquivo_audio, language=idioma)
    except Exception as e:
        logger.error(f"Erro ao carregar o modelo Whisper: {e}")
        raise

    return resultado.get("segments", [])

def obter_caminho_audio():
    parser = argparse.ArgumentParser(description="Script para transcrição e diarização.")
    parser.add_argument("arquivo_audio", type=str, help="Caminho do arquivo de áudio para processar.")
    args = parser.parse_args()
    return args.arquivo_audio

if __name__ == "__main__":
    # Carregar o token do arquivo .env ou variável de ambiente
    from dotenv import load_dotenv
    load_dotenv()

    token = os.getenv("HF_AUTH_TOKEN")
    if not token:
        token = input("Digite seu token do Hugging Face: ")
    if not validar_token(token):
        logger.error("Token inválido. Saindo...")
        exit(1)

    arquivo = obter_caminho_audio()
    try:
        validar_pacotes_python()
        start_time = time.time()
        logger.info("🚀 Iniciando transcrição do áudio.")
        transcricao = transcrever_audio(arquivo)
        elapsed_time = time.time() - start_time
        output_path = os.path.splitext(os.path.basename(arquivo))[0] + "_transcricao.txt"
        with open(output_path, "w", encoding="utf-8") as f:
            for item in transcricao:
                linha = f"[{item['start']:.2f} - {item['end']:.2f}] {item['text']}\n"
                f.write(linha)
        logger.info(f"Transcrição salva com sucesso no arquivo: {output_path}")
        logger.info(f"Transcrição concluída em {elapsed_time:.2f} segundos.")
        logger.info("✅ Transcrição concluída.")
    except Exception as e:
        logger.error(f"Erro ao transcrever o áudio: {e}")

