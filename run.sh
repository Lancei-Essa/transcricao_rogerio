#!/bin/bash

# ----------------------------------------------------
# Script de Execução para Transcrição Podcast
# Autor: [Seu Nome]
# Data de Criação: [Data]
# Versão: 1.2.0
# Documentação: [Link para a documentação]
# ----------------------------------------------------

VENV_DIR="venv"
PYTHON_EXEC=${PYTHON_EXEC:-python3}

# Verificar se o ambiente virtual está configurado
if [ ! -d "$VENV_DIR" ]; then
    echo "Erro: Ambiente virtual não encontrado. Execute o setup.sh primeiro."
    exit 1
fi

# Ativar o ambiente virtual
if [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "darwin"* ]]; then
    ACTIVATE_SCRIPT="source $VENV_DIR/bin/activate"
elif [[ "$OSTYPE" == "cygwin" || "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    ACTIVATE_SCRIPT="$VENV_DIR\\Scripts\\activate"
else
    echo "Sistema operacional não suportado: $OSTYPE"
    exit 1
fi

eval "$ACTIVATE_SCRIPT"

# Executar o programa principal
$PYTHON_EXEC main.py || echo "Erro ao executar o programa principal."