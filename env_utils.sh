#!/bin/bash

# Function to log messages
log() {
    local LEVEL=${2:-INFO} # Nível padrão é INFO
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$LEVEL] $1"
}

# Function to clean logs older than 30 days
clean_logs() {
    log "Limpando logs antigos..."
    find "$LOGS_DIR" -type f -mtime +30 -exec gzip {} \; || log "Erro ao limpar logs antigos." ERROR
}

# Function to check if the script is run with sudo
check_sudo() {
    if [ "$EUID" -ne 0 ]; then
        log "Por favor, execute este comando com sudo." ERROR
        exit 1
    fi
}

# Function to validate Python version
validate_python_version() {
    CURRENT_PYTHON=$($PYTHON_EXEC --version | awk '{print $2}')
    if [[ $(echo -e "$REQUIRED_PYTHON\n$CURRENT_PYTHON" | sort -V | head -n1) != "$REQUIRED_PYTHON" ]]; then
        log "Python $REQUIRED_PYTHON ou superior é necessário. Versão atual: $CURRENT_PYTHON" ERROR
        exit 1
    fi
}

# Function to create a virtual environment
create_venv() {
    SECONDS=0
    log "Criando ambiente virtual..."
    python3 -m venv "$VENV_DIR"
    log "Ambiente virtual criado em $SECONDS segundos."
}

# Function to activate a virtual environment
activate_venv() {
    log "Ativando ambiente virtual..."
    source "$VENV_DIR/bin/activate"
    log "Ambiente virtual ativado."
}

# Function to check internet connectivity
check_internet() {
    log "Verificando conexão com a internet..."
    if ! curl -s --head https://google.com | grep -E "200 OK|301 Moved Permanently" > /dev/null; then
        log "Erro: Sem conexão com a internet. Verifique sua conexão." ERROR
        exit 1
    fi
    log "Conexão com a internet confirmada."
}

# Function to validate system dependencies
validate_system_dependencies() {
    log "Validando dependências do sistema..."
    for cmd in curl python3; do
        if ! command -v $cmd &> /dev/null; then
            log "Erro: $cmd não está instalado. Por favor, instale antes de continuar." ERROR
            exit 1
        fi
    done
    log "✔ Todas as dependências do sistema estão instaladas."
}

# Function to validate virtual environment
validate_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        log "Erro: Ambiente virtual não encontrado. Certifique-se de que foi criado corretamente." ERROR
        exit 1
    fi
    log "✔ Ambiente virtual encontrado."
}

# Function to install Python dependencies
install_python_dependencies() {
    log "Instalando dependências Python..."
    pip install -r requirements.txt || { log "Erro ao instalar dependências Python." ERROR; exit 1; }
    log "✔ Dependências Python instaladas."
}

# Function to validate Python dependencies
validate_python_dependencies() {
    log "Validando dependências Python..."
    pip check || { log "Erro: Dependências Python não estão corretas." ERROR; exit 1; }
    log "✔ Dependências Python validadas."
}
