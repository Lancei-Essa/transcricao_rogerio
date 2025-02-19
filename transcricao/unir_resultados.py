def unir_transcricao_diarizacao(transcricao_texto, segmentos):
    """
    Une a transcrição e a diarização, pareando os trechos corretamente.
    
    Args:
        transcricao_texto (str): Texto da transcrição bruta.
        segmentos (list): Lista de segmentos da diarização no formato [(inicio, fim, speaker)].

    Returns:
        str: Transcrição formatada com falantes e timestamps.
    """

    linhas_transcricao = transcricao_texto.split("\n")  # Divide a transcrição em linhas
    transcricao_formatada = []

    for i, (inicio, fim, speaker) in enumerate(segmentos):
        if i < len(linhas_transcricao):
            linha_texto = linhas_transcricao[i]
        else:
            linha_texto = "[TEXTO INDISPONÍVEL]"

        trecho = f"[{inicio:.2f} - {fim:.2f}] {speaker}: {linha_texto}"
        transcricao_formatada.append(trecho)

    return "\n".join(transcricao_formatada)
