import os

# Diretório do modelo offline do Whisper
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'modelos', 'whisper-large-v2')

# Diretório onde os áudios extraídos serão salvos
AUDIO_DIR = os.path.join(os.path.dirname(__file__), 'audio')

# Diretório de logs
LOGS_DIR = os.path.join(os.path.dirname(__file__), 'logs')

# Diretório das transcrições
TRANSCRICOES_DIR = os.path.join(os.path.dirname(__file__), 'transcricao')

