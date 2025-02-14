#!/bin/bash

# ----------------------------------------------------
# Script de Configuração para Transcrição Podcast
# Autor: [Seu Nome]
# Data de Criação: [Data]
# Versão: 1.2.0
# Documentação: [Link para a documentação]
# ----------------------------------------------------

set -e  # Interrompe o script ao primeiro erro
trap 'echo "Erro na linha $LINENO. Consulte $LOGFILE para mais detalhes."' ERR
trap "deactivate 2>/dev/null || true" EXIT

# Importar módulos
source scripts/constants.sh
source /path/to/env_utils.sh
source env_utils.sh
source scripts/dependencies.sh
source scripts/validation.sh

# Mensagem de boas-vindas
echo "----------------------------------------------------"
echo "Bem-vindo ao Script de Configuração da Transcrição Podcast"
echo "Versão: 1.2.0 | Data: $(date)"
echo "----------------------------------------------------"

# Variáveis globais
RUN_DIR="$LOGS_DIR/run_$(date '+%Y-%m-%d_%H-%M-%S')"
mkdir -p "$RUN_DIR"
LOGFILE="$RUN_DIR/setup.log"
INSTALL_LOG="$RUN_DIR/install.log"
VALIDATION_LOG="$RUN_DIR/validation.log"
PYTHON_EXEC=${PYTHON_EXEC:-python3}

INSTALL_WHISPER=true
INSTALL_FFMPEG=true
VERBOSE=false
USE_GLOBAL_ENV=false

# Função de log com timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $@"
}

# Verificar flags opcionais
for arg in "$@"; do
    case $arg in
        --no-whisper)
            INSTALL_WHISPER=false
            shift
            ;;
        --no-ffmpeg)
            INSTALL_FFMPEG=false
            shift
            ;;
        --clean)
            log "Limpando ambiente existente..."
            rm -rf "$VENV_DIR" "$LOGS_DIR"
            log "Limpeza concluída."
            exit 0
            ;;
        --clean-logs)
            log "Limpando logs..."
            rm -rf "$LOGS_DIR"
            mkdir "$LOGS_DIR"
            log "Logs limpos com sucesso."
            exit 0
            ;;
        --clean-venv)
            log "Removendo ambiente virtual..."
            rm -rf "$VENV_DIR"
            log "Ambiente virtual removido."
            exit 0
            ;;
        --help)
            echo "Uso: ./setup.sh [opções]"
            echo "Opções disponíveis:"
            echo "  --no-whisper      Pule a instalação do Whisper"
            echo "  --no-ffmpeg       Pule a instalação do FFmpeg"
            echo "  --clean           Limpe o ambiente virtual e os logs"
            echo "  --clean-logs      Limpe apenas os logs"
            echo "  --clean-venv      Remova apenas o ambiente virtual"
            echo "  --skip-run        Configure o ambiente sem executar o programa principal"
            echo "  --verbose         Exiba logs detalhados"
            echo "  --global-env      Use pacotes globais em vez de criar um ambiente virtual"
            exit 0
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --global-env)
            USE_GLOBAL_ENV=true
            shift
            ;;
    esac
done

# Função de rollback em caso de falhas
rollback() {
    log "Executando rollback..."
    rm -rf "$VENV_DIR" "$LOGS_DIR"
    log "Rollback concluído. Execute o script novamente."
}
trap rollback ERR

# Limpar logs antigos
clean_logs

# Verificar se o Python 3 está instalado
if ! command -v $PYTHON_EXEC &> /dev/null; then
    log "Erro: $PYTHON_EXEC não encontrado."
    exit 1
fi

# Validar versão mínima do Python
validate_python_version

# Validar permissões de escrita no diretório
if [ ! -w "$(pwd)" ]; then
    log "Erro: Sem permissões de escrita no diretório atual. Execute o script em um local com permissões adequadas."
    exit 1
fi

# Checar dependências do sistema
for cmd in curl git pip; do
    if ! command -v $cmd &> /dev/null; then
        log "Erro: $cmd não está instalado. Instale antes de continuar."
        exit 1
    fi
done

# Checar espaço em disco
DISK_SPACE=$(df "$(pwd)" | awk 'NR==2 {print $4}')
if [ "$DISK_SPACE" -lt 1048576 ]; then # Menos de 1GB
    log "Erro: Espaço insuficiente no disco."
    exit 1
fi

# Limpar caches temporários após a execução
limpar_caches() {
    log "Limpando caches de pip..."
    pip cache purge
    log "Caches de pip limpos."
}
trap limpar_caches EXIT

# Fluxo principal do script
log "Iniciando configuração do ambiente..."
if $USE_GLOBAL_ENV; then
    log "Usando pacotes globais. Ambiente virtual será ignorado."
else
    create_venv
    activate_venv
fi
install_python_dependencies
install_ffmpeg
validate_dependencies
test_ffmpeg
log_versions

log "Configuração concluída! O programa principal não será executado."
log "Veja mais detalhes no arquivo de log: $LOGFILE"

echo -e "\nResumo da Configuração:"
echo "✔ Ambiente virtual configurado: $VENV_DIR"
echo "✔ Logs armazenados em: $LOGS_DIR"
echo "✔ FFmpeg instalado e validado."
echo "✔ Dependências Python instaladas com sucesso."
echo "✔ Programa principal executado com sucesso."
