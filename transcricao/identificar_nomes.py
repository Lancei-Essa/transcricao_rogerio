import re
import logging

def configurar_logs():
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
    return logging.getLogger(__name__)

logger = configurar_logs()

def identificar_nomes(transcricao):
    """
    Identifica nomes de falantes na transcrição e substitui os identificadores SPEAKER_X pelo nome correto.

    :param transcricao: Texto da transcrição já sincronizada.
    :return: Transcrição com os nomes corrigidos.
    """

    # Padrões para identificar nomes
    padrao_apresentacao = re.compile(
        r"(Meu nome (?:completo )?\u00e9|Eu sou|Chamo-me|Sou(?:\s+o|a)?|Podem me chamar de|Me chamam de|Este é|Aqui comigo está)\s+([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)",
        re.IGNORECASE
    )
    padrao_chamado = re.compile(
        r"(?:\b(?:Obrigado|Bem-vindo|Falo aqui com|Este é|Recebemos hoje)\s+)([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)",
        re.IGNORECASE
    )
    padrao_speaker = re.compile(
        r"(\[\d{2}:\d{2}:\d{2}\.\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}\.\d{3}\])\s*(SPEAKER_\d+)\s*:",
        re.IGNORECASE
    )

    nomes_por_speaker = {}
    nomes_identificados = []
    linhas_processadas = []
    
    # Primeiro, identificar quem se apresenta
    for linha in transcricao.split("\n"):
        match_speaker = padrao_speaker.match(linha)
        
        # Detectar apresentações ("Meu nome é João Silva", "Eu sou Luiz Felipe Guerra")
        match_apresentacao = padrao_apresentacao.search(linha)
        if match_speaker and match_apresentacao:
            speaker_id = match_speaker.group(2)
            nome = match_apresentacao.group(2)  # Captura o nome completo
            
            if speaker_id not in nomes_por_speaker:
                nomes_por_speaker[speaker_id] = nome
                nomes_identificados.append(nome)
                logger.debug(f"🔍 Nome identificado na apresentação: {nome} ({speaker_id})")
        
        # Detectar quando um nome é mencionado diretamente
        match_chamado = padrao_chamado.search(linha)
        if match_chamado:
            nome_mencionado = match_chamado.group(1)
            nomes_identificados.append(nome_mencionado)
            logger.debug(f"🔍 Nome mencionado em conversa: {nome_mencionado}")

        linhas_processadas.append(linha)
    
    logger.debug(f"📌 Todos os nomes identificados: {', '.join(nomes_identificados) if nomes_identificados else 'Nenhum nome identificado'}")
    logger.debug(f"📌 Associação entre SPEAKER_X e nomes identificados: {nomes_por_speaker}")
    
    # Agora substituir SPEAKER_X pelos nomes identificados
    transcricao_corrigida = []
    for linha in linhas_processadas:
        for speaker, nome in nomes_por_speaker.items():
            if speaker in linha:
                logger.debug(f"📝 Substituindo {speaker} por {nome}")
            linha = linha.replace(speaker, nome)
        transcricao_corrigida.append(linha)

    transcricao_final = "\n".join(transcricao_corrigida)
    
    logger.debug("✅ Transcrição final corrigida:")
    print(transcricao_final)
    
    return transcricao_final

# Teste rápido com transcrição simulada
teste_transcricao = """
[00:11.700 --> 00:16.900] SPEAKER_00: Meu nome é Luiz Felipe Guerra, sou um dos participantes aqui.
[00:24.080 --> 00:28.500] SPEAKER_00: E hoje eu trouxe um grande convidado, primeiro investidor da minha startup, Dudos Cartesini.
[00:42.340 --> 00:44.380] SPEAKER_01: Dudos, muito obrigado por você estar aqui.
"""
resultado = identificar_nomes(teste_transcricao)
print("\n📌 Transcrição Final:\n", resultado)
