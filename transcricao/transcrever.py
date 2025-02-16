import whisper
import os
import time
from tqdm import tqdm
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def transcrever_audio(caminho_audio):
    logger.debug("🔄 Carregando modelo Whisper...")
    model = whisper.load_model("large-v2")
    logger.debug("✅ Modelo carregado!")

    if not os.path.exists(caminho_audio):
        logger.error(f"❌ Arquivo não encontrado: {caminho_audio}")
        return None

    logger.debug(f"🎙️ Transcrevendo {caminho_audio}...")

    # Estimativa do tempo total com base na duração do áudio (1x tempo real)
    duracao_audio = os.path.getsize(caminho_audio) / (16 * 16000)  # Estima com base no tamanho do arquivo
    duracao_estimada = max(duracao_audio, 60)  # Tempo mínimo estimado de 60s para progresso

    logger.debug(f"⏳ Tempo estimado de transcrição: {int(duracao_estimada // 60)} min {int(duracao_estimada % 60)} seg")

    # Criando barra de progresso manual (porque tqdm não capta a transcrição do Whisper)
    progresso = tqdm(total=duracao_estimada, desc="📝 Transcrevendo", ncols=80)
    
    try:
        start_time = time.time()
        result = model.transcribe(caminho_audio, verbose=True)  # Mostra a transcrição no terminal em tempo real
        elapsed_time = time.time() - start_time
        
        progresso.update(duracao_estimada)  # Atualiza progresso ao final
        progresso.close()
        
        logger.debug(f"✅ Transcrição concluída! Tempo total: {int(elapsed_time // 60)} min {int(elapsed_time % 60)} seg")
        
        # Salvar a transcrição
        caminho_txt = os.path.splitext(caminho_audio)[0] + ".txt"
        with open(caminho_txt, "w", encoding="utf-8") as f:
            f.write(result["text"])

        logger.debug(f"📄 Transcrição salva em: {caminho_txt}")
        return caminho_txt

    except KeyboardInterrupt:
        progresso.close()
        logger.error("\n❌ Transcrição interrompida pelo usuário.")
        return None

    except Exception as e:
        progresso.close()
        logger.error(f"❌ Erro durante a transcrição: {e}")
        return None

