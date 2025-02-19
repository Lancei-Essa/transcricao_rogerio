import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def salvar_transcricao(caminho_audio, texto_transcricao):
    """
    Salva a transcrição em um arquivo de texto na mesma pasta do áudio original.

    :param caminho_audio: Caminho do arquivo de áudio processado.
    :param texto_transcricao: Texto transcrito a ser salvo.
    :return: Caminho do arquivo salvo.
    """
    if not texto_transcricao or not isinstance(texto_transcricao, str):
        logger.warning("⚠️ Nenhum texto válido foi passado para salvar.")
        return None

    caminho_txt = caminho_audio.replace(".wav", ".txt")
    logger.debug(f"💾 Salvando transcrição em: {caminho_txt}")

    try:
        with open(caminho_txt, "w", encoding="utf-8") as arquivo:
            arquivo.write(texto_transcricao)
        logger.debug("✅ Transcrição salva com sucesso!")
    except Exception as e:
        logger.error(f"❌ Erro ao salvar transcrição: {e}")
        return None

    return caminho_txt
