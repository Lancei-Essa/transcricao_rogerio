# transcricao/formatar_tempo.py
from datetime import timedelta

def formatar_tempo(segundos):
    """Converte segundos para o formato hh:mm:ss.sss"""
    tempo = str(timedelta(seconds=segundos))
    if "." in tempo:
        tempo, ms = tempo.split(".")
        return f"{tempo}.{ms[:3]}"  # Mantém três casas decimais nos milissegundos
    return f"{tempo}.000"
