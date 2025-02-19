import re
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def sincronizar_diarizacao_com_transcricao(segmentos, texto_transcrito):
    """
    Sincroniza a transcrição com os segmentos de áudio identificados na diarização.
    
    :param segmentos: Lista de tuplas (inicio, fim, speaker) da diarização.
    :param texto_transcrito: Texto completo transcrito.
    :return: Texto formatado com falantes e timestamps sincronizados.
    """
    if isinstance(texto_transcrito, list):  
        texto_transcrito = "\n".join(texto_transcrito)  # Converte lista para string, caso necessário

    transcricao_formatada = ""
    linhas_transcricao = texto_transcrito.strip().split("\n")  # Divide a transcrição por linha

    # Exibir logs para depuração
    logger.debug(f"📌 Segmentos de diarização detectados: {len(segmentos)}")
    logger.debug(f"📌 Linhas de transcrição detectadas: {len(linhas_transcricao)}")

    # Se houver desencontro entre os tamanhos, logamos um aviso
    if len(segmentos) != len(linhas_transcricao):
        logger.warning(f"⚠️ Alerta: Número de segmentos de áudio ({len(segmentos)}) e linhas de transcrição ({len(linhas_transcricao)}) não coincidem!")

    # Associa cada segmento de tempo a uma linha de transcrição
    for i, (segmento, linha) in enumerate(zip(segmentos, linhas_transcricao)):
        inicio, fim, speaker = segmento
        trecho = f"[{inicio:.2f} - {fim:.2f}] {speaker}: {linha}\n"
        transcricao_formatada += trecho
        logger.debug(f"✅ Trecho {i}: {trecho.strip()}")

    return transcricao_formatada
