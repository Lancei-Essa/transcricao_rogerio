import re
import logging

def configurar_logs():
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    return logging.getLogger(__name__)

logger = configurar_logs()

def sincronizar_diarizacao_com_transcricao(segmentos, texto_transcrito):
    """
    Sincroniza a transcrição com os segmentos de áudio identificados na diarização.

    :param segmentos: Lista de tuplas (inicio, fim, speaker) da diarização.
    :param texto_transcrito: Texto completo transcrito.
    :return: Texto formatado com falantes e timestamps sincronizados.
    """
    if isinstance(texto_transcrito, list):  
        texto_transcrito = "\n".join([str(linha) for linha in texto_transcrito])
    
    transcricao_formatada = ""
    linhas_transcricao = texto_transcrito.strip().split("\n")
    
    logger.info(f"📌 Segmentos de diarização detectados: {len(segmentos)}")
    logger.info(f"📌 Linhas de transcrição detectadas: {len(linhas_transcricao)}")
    
    if not segmentos or not linhas_transcricao:
        logger.warning("⚠️ Não há dados suficientes para sincronização.")
        return texto_transcrito

    index_transcricao = 0
    transcricao_por_falante = []
    tolerancia = 0.2
    falante_anterior = None

    for inicio_d, fim_d, falante in segmentos:
        if not falante:
            logger.warning(f"⚠️ Falante não identificado no segmento [{inicio_d:.2f} - {fim_d:.2f}]. Atribuindo 'Speaker Desconhecido'.")
            falante = "Speaker Desconhecido"

        trecho_falante = []
        while index_transcricao < len(linhas_transcricao):
            linha = linhas_transcricao[index_transcricao]
            # Expressão regular melhorada para capturar timestamps e conteúdo
            match = re.match(r"\[\s*(\d+\.\d{1,3})\s*-\s*(\d+\.\d{1,3})\s*\]\s*(.+)", linha)
            if not match:
                if linhas_ignoradas < 5:
                    logger.warning(f"⚠️ Linha ignorada por formato inesperado: {linha}")
                elif linhas_ignoradas == 5:
                    logger.warning("⚠️ Mais linhas foram ignoradas por formato inesperado. Suprimindo mensagens adicionais.")
                linhas_ignoradas += 1
                index_transcricao += 1  # Avança para evitar loop infinito
                continue

            inicio_t, fim_t, conteudo = float(match.group(1)), float(match.group(2)), match.group(3)

            # Verifica se há interseção de tempo com tolerância ajustada
            if not (fim_t < inicio_d - tolerancia or inicio_t > fim_d + tolerancia):
                trecho_falante.append(conteudo.strip())
                index_transcricao += 1  # Avançar apenas quando houver correspondência
            else:
                break  # Sai do loop se passar do tempo do segmento atual

        if trecho_falante:
            transcricao_por_falante.append(f"\n[{inicio_d:.2f} - {fim_d:.2f}] {falante}:\n" + "\n".join(trecho_falante) + "\n")

    transcricao_formatada = "\n".join(transcricao_por_falante).strip()

    logger.debug(f"✅ Transcrição sincronizada concluída!")

    # Exibir resumo da transcrição final
    total_linhas = len(transcricao_formatada.split("\n"))
    print(f"\n🔍 Transcrição Final: {total_linhas} linhas geradas.")
    print("📄 Prévia das 5 primeiras linhas:\n")
    print("\n".join(transcricao_formatada.split("\n")[:5]))  # Mostra apenas as 5 primeiras linhas para conferência

    return transcricao_formatada
