#!/bin/bash

# ----------------------------------------------------
# Script de Configuração para Transcrição Podcast
# Autor: [Seu Nome]
# Data de Criação: [Data]
# Versão: 1.2.0
# Documentação: [Link para a documentação]
# ----------------------------------------------------

set -e  # Interrompe o script ao primeiro erro
set -x  # Adiciona log detalhado de todos os comandos
trap 'custom_log "Erro na linha $LINENO. Consulte $LOGFILE para mais detalhes."' ERR
trap "deactivate 2>/dev/null || true" EXIT

# Function to log messages with severity levels
custom_log() {
    local LEVEL=${2:-INFO} # Nível padrão é INFO
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$LEVEL] $1"
}

# Inicialização das variáveis críticas
LOGS_DIR="logs"
VENV_DIR="venv"

# Validação das variáveis críticas
if [ -z "$LOGS_DIR" ]; then
    echo "Erro: LOGS_DIR não está definido. Verifique o script."
    exit 1
fi

if [ -z "$VENV_DIR" ]; then
    echo "Erro: VENV_DIR não está definido. Verifique o script."
    exit 1
fi

# Debug messages
echo "LOGS_DIR está definido como: $LOGS_DIR"
echo "VENV_DIR está definido como: $VENV_DIR"

LOGFILE="logs/setup_$(date '+%Y-%m-%d_%H-%M-%S').log"
INSTALL_LOG="logs/install_$(date '+%Y-%m-%d_%H-%M-%S').log"
VALIDATION_LOG="logs/validation_$(date '+%Y-%m-%d_%H-%M-%S').log"

# Criação dos diretórios necessários
mkdir -p "$LOGS_DIR"
chmod -R 755 "$LOGS_DIR"
custom_log "✔ Permissões configuradas para o diretório de logs."

exec > >(tee -a "$LOGFILE") 2> >(tee -a "$INSTALL_LOG" >&2)

FFMPEG_DOWNLOAD_URL="https://ffmpeg.org/download.html"
REQUIRED_PYTHON="3.10"
PYTHON_EXEC=${PYTHON_EXEC:-python3}

INSTALL_WHISPER=true
INSTALL_FFMPEG=true

# Function to check internet connectivity
check_internet() {
    custom_log "Verificando conexão com a internet..."
    if ping -c 1 -W 2 8.8.8.8 > /dev/null 2>&1; then
        custom_log "✔ Conexão com a internet confirmada."
    else
        custom_log "Erro: Sem conexão com a internet. Verifique sua conexão." ERROR
        exit 1
    fi
}

install_rust() {
    custom_log "Verificando instalação do Rust..."
    if ! command -v rustup &> /dev/null; then
        custom_log "Rustup não encontrado. Instalando Rustup..."
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
        export PATH="$HOME/.cargo/bin:$PATH"  # Adiciona o Rust ao PATH temporariamente

        # Garantir que o PATH seja configurado permanentemente
        SHELL_CONFIG="$HOME/.bashrc"
        if [ "$SHELL" == "/bin/zsh" ]; then
            SHELL_CONFIG="$HOME/.zshrc"
        fi
        
        if ! grep -q 'export PATH="$HOME/.cargo/bin:$PATH"' "$SHELL_CONFIG"; then
            echo 'export PATH="$HOME/.cargo/bin/$PATH"' >> "$SHELL_CONFIG"
        fi
        
        # Recarregar o ambiente do shell
        source "$SHELL_CONFIG"

        custom_log "✔ Rustup instalado com sucesso."
    else
        custom_log "✔ Rustup já está instalado."
    fi

    if ! command -v cargo &> /dev/null; then
        custom_log "Erro: Cargo não está no PATH. Verifique as configurações do ambiente." ERROR
        exit 1
    fi

    custom_log "Atualizando Rust para a versão mais recente..." INFO
    rustup update stable

    # Validar instalação do Rust
    if ! rustup --version &> /dev/null; then
        custom_log "Erro: A instalação do Rust falhou. Por favor, verifique manualmente." ERROR
        exit 1
    fi

    custom_log "✔ Rust configurado corretamente." INFO
}

# Garantir arquitetura correta para Apple Silicon
rustup target add aarch64-apple-darwin
export CARGO_BUILD_TARGET=aarch64-apple-darwin

# Adicionar flags de compilação (opcional)
export RUSTFLAGS="-C target-cpu=native"

# Function to validate system dependencies
validate_system_dependencies() {
    custom_log "Validando dependências do sistema..."
    for cmd in curl python3; do
        if ! command -v $cmd &> /dev/null; then
            custom_log "Erro: $cmd não está instalado. Por favor, instale antes de continuar." ERROR
            exit 1
        fi
    done
    custom_log "✔ Todas as dependências do sistema estão instaladas."
}

# Function to create, validate, and activate virtual environment
custom_log "Atualizando pip globalmente..."
$PYTHON_EXEC -m pip install --upgrade pip || {
    custom_log "Erro ao atualizar o pip globalmente. Verifique manualmente." ERROR
    exit 1
}
custom_log "✔ pip global atualizado com sucesso."

custom_log "Verificando suporte do Python para 'venv'..."
if ! $PYTHON_EXEC -m ensurepip &>/dev/null; then
    custom_log "Erro: O Python atual ($PYTHON_EXEC) não suporta a criação de ambientes virtuais. Verifique a instalação do Python." ERROR
    exit 1
fi
custom_log "✔ Python suporta 'venv'."

setup_virtualenv() {
    custom_log "Verificando se o ambiente virtual já existe..."
    if [ -d "$VENV_DIR" ]; then
        custom_log "Ambiente virtual existente detectado. Removendo..."
        rm -rf "$VENV_DIR"
    fi

    custom_log "Criando o ambiente virtual..."
    $PYTHON_EXEC -m venv "$VENV_DIR" || {
        custom_log "Erro ao criar o ambiente virtual. Verifique se o Python suporta 'venv'." ERROR
        exit 1
    }
    custom_log "✔ Ambiente virtual criado com sucesso."

    custom_log "Ativando o ambiente virtual..."
    source "$VENV_DIR/bin/activate" || {
        custom_log "Erro ao ativar o ambiente virtual. Verifique o diretório: $VENV_DIR" ERROR
        exit 1
    }
    custom_log "✔ Ambiente virtual ativado com sucesso."

    custom_log "Atualizando pip, setuptools e wheel no ambiente virtual..."
    pip install --upgrade pip setuptools wheel || {
        custom_log "Erro ao atualizar pip, setuptools e wheel no ambiente virtual." ERROR
        exit 1
    }
    custom_log "✔ pip, setuptools e wheel atualizados no ambiente virtual."
}

# Function to validate Python packages
validate_python_packages() {
    custom_log "Validando pacotes Python necessários..." INFO
    for pacote in PySide6 invoke pytest requests transformers pyannote.audio; do
        custom_log "Verificando instalação de $pacote..." INFO
        if ! python -c "import $pacote" &> /dev/null; then
            custom_log "Erro: O pacote $pacote não está instalado. Tentando instalar..."
            pip install "$pacote" || {
                custom_log "Erro ao instalar $pacote. Verifique manualmente." ERROR
                exit 1
            }
        else
            custom_log "✔ Pacote $pacote já está instalado." INFO
        fi
    done
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
            custom_log "Limpando ambiente existente..."
            rm -rf "$VENV_DIR" "$LOGS_DIR"
            custom_log "Limpeza concluída."
            exit 0
            ;;
        --clean-logs)
            custom_log "Limpando logs..."
            rm -rf "$LOGS_DIR"
            mkdir "$LOGS_DIR"
            custom_log "Logs limpos com sucesso."
            exit 0
            ;;
        --clean-venv)
            custom_log "Removendo ambiente virtual..."
            rm -rf "$VENV_DIR"
            custom_log "Ambiente virtual removido."
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
            echo "Exemplo:"
            echo "  ./setup.sh --no-ffmpeg"
            echo "  ./setup.sh --clean"
            exit 0
            ;;
    esac
done

# Função de rollback em caso de falhas
rollback() {
    custom_log "Executando rollback..."
    rm -rf "$VENV_DIR" "$LOGS_DIR"
    custom_log "Rollback concluído. Execute o script novamente."
}
trap rollback ERR

# Limpar logs antigos
custom_log "Limpando logs antigos..." INFO
find "$LOGS_DIR" -type f -mtime +30 -exec rm -f {} \; || custom_log "Erro ao limpar logs antigos." ERROR

# Compactar logs antigos
custom_log "Compactando logs antigos..." INFO
find "$LOGS_DIR" -type f -mtime +30 -exec gzip {} \; || custom_log "Erro ao compactar logs antigos." ERROR
custom_log "✔ Logs antigos compactados com sucesso." INFO

# -------------------------------
# Funções relacionadas à configuração inicial
# -------------------------------

# Função para verificar permissões de administrador
check_sudo() {
    if [ "$EUID" -ne 0 ]; then
        custom_log "Este comando exige privilégios administrativos para certas operações (e.g., instalação do FFmpeg)." ERROR
        exit 1
    fi
}

# Verificar conexão com a internet
check_internet

# Instalar Rust
install_rust

# Instalar ferramentas de linha de comando do Xcode no macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    xcode-select --install || true
fi

# Verificar se o Python 3 está instalado
if ! command -v $PYTHON_EXEC &> /dev/null; then
    custom_log "Erro: $PYTHON_EXEC não encontrado." ERROR
    exit 1
fi

# Validar versão mínima do Python
CURRENT_PYTHON=$($PYTHON_EXEC --version | awk '{print $2}')
if [[ $(echo -e "$REQUIRED_PYTHON\n$CURRENT_PYTHON" | sort -V | head -n1) != "$REQUIRED_PYTHON" ]]; then
    custom_log "Python $REQUIRED_PYTHON ou superior é necessário. Versão atual: $CURRENT_PYTHON" ERROR
    exit 1
fi

# Validar permissões de escrita no diretório
if [ ! -w "$(pwd)" ]; then
    custom_log "Erro: Sem permissões de escrita no diretório atual. Execute o script em um local com permissões adequadas." ERROR
    exit 1
fi

# -------------------------------
# Funções relacionadas à instalação de dependências
# -------------------------------

source env_utils.sh

# Verificar se o arquivo requirements.txt existe
if [ ! -f "requirements.txt" ]; then
    custom_log "Arquivo requirements.txt não encontrado. Por favor, adicione-o antes de prosseguir." ERROR
    exit 1
fi

# Atualizar e completar o requirements.txt
if [ ! -s "requirements.txt" ]; then
    cat <<EOL > requirements.txt
PySide6==6.5.2
invoke==1.7.3
pytest==7.2.2
requests==2.31.0
transformers==4.21.0
pyannote.audio==2.1.1
whisper>=2022.12.11
loguru>=0.5.3
moviepy>=1.0.3
pydub>=0.25.1
torch>=1.9 --index-url https://download.pytorch.org/whl/cpu
EOL
    custom_log "Arquivo requirements.txt criado com sucesso." INFO
else
    custom_log "Arquivo requirements.txt já existe." INFO
fi

# Instalar dependências
custom_log "Instalando dependências do requirements.txt..."
pip install --upgrade pip setuptools wheel || {
    custom_log "Erro ao atualizar pip, setuptools ou wheel. Verifique o log em $INSTALL_LOG" ERROR
    exit 1
}

pip install --force-reinstall --no-cache-dir -r requirements.txt || {
    custom_log "Erro ao instalar dependências do requirements.txt. Verifique o log em $INSTALL_LOG" ERROR
    exit 1
}
custom_log "✔ Dependências instaladas com sucesso."

custom_log "Verificando instalação do PyTorch..."
if ! python -c "import torch" &> /dev/null; then
    custom_log "Erro: O pacote 'torch' não foi instalado corretamente. Tente novamente." ERROR
    exit 1
fi
custom_log "✔ PyTorch instalado corretamente."

install_python_dependencies() {
    custom_log "Atualizando pip, setuptools e wheel..." INFO
    pip install --upgrade pip setuptools wheel || {
        custom_log "Erro ao atualizar pip, setuptools e wheel." ERROR
        exit 1
    }

    custom_log "Instalando dependências do requirements.txt..." INFO
    pip install --use-pep517 --force-reinstall --no-cache-dir -r requirements.txt || {
        custom_log "Erro ao instalar dependências do requirements.txt. Ignorando pacotes problemáticos." WARNING
    }

    custom_log "Reinstalando pacotes problemáticos diretamente..." INFO
    export CXX=clang++
    export CC=clang
    pip install --force-reinstall hmmlearn==0.2.7 tokenizers || {
        custom_log "Erro ao reinstalar pacotes problemáticos." ERROR
        exit 1
    }

    custom_log "Instalando o Whisper diretamente do GitHub..." INFO
    pip install --no-cache-dir git+https://github.com/openai/whisper.git || {
        custom_log "Erro ao instalar o Whisper do GitHub." ERROR
        exit 1
    }

    custom_log "✔ Todas as dependências Python instaladas com sucesso." INFO
}

# Função para instalar dependências
instalar_dependencias() {
    if [ -z "$VIRTUAL_ENV" ]; then
        custom_log "Erro: O ambiente virtual não está ativado. Por favor, ative o ambiente antes de continuar." ERROR
        exit 1
    fi

    custom_log "Atualizando pip, setuptools e wheel..." INFO
    pip install --upgrade pip setuptools wheel

    if [ ! -f "requirements.txt" ]; then
        custom_log "Arquivo requirements.txt não encontrado. Por favor, adicione-o antes de prosseguir." ERROR
        exit 1
    fi

    custom_log "Instalando dependências do requirements.txt... Isso pode levar alguns minutos. Por favor, aguarde." INFO
    pip install -r requirements.txt || {
        custom_log "Erro ao instalar dependências do requirements.txt. Verifique o arquivo $INSTALL_LOG para mais detalhes." ERROR
    }

    if [[ "$INSTALL_WHISPER" == true ]]; then
        custom_log "Instalando o Whisper..." INFO
        pip install --no-cache-dir git+https://github.com/openai/whisper.git

        if ! $PYTHON_EXEC -c "import whisper" &> /dev/null; then
            custom_log "Erro: Whisper não foi instalado corretamente." ERROR
            exit 1
        fi
    else
        custom_log "Instalação do Whisper foi pulada." INFO
    fi
}

# Função para configurar o FFmpeg
configurar_ffmpeg() {
    if [[ "$INSTALL_FFMPEG" == true ]]; then
        custom_log "Verificando instalação do FFmpeg..." INFO
        if ! command -v ffmpeg &> /dev/null; then
            custom_log "FFmpeg não encontrado. Tentando instalar..." INFO
            check_sudo
            if [[ "$OSTYPE" == "linux-gnu"* ]]; then
                sudo -H apt update && sudo -H apt install -y ffmpeg || {
                    custom_log "Erro ao instalar o FFmpeg. Verifique suas permissões." ERROR
                    exit 1
                }
            elif [[ "$OSTYPE" == "darwin"* ]]; then
                if ! command -v brew &> /dev/null; then
                    custom_log "Erro: Homebrew não está instalado. Instale manualmente in https://brew.sh." ERROR
                    exit 1
                fi
                brew install ffmpeg || {
                    custom_log "Erro ao instalar o FFmpeg com brew." ERROR
                    exit 1
                }
            fi
        else
            custom_log "✔ FFmpeg já instalado." INFO
        fi
    else
        custom_log "Instalação do FFmpeg foi pulada." INFO
    fi
}

# Função para criar o diretório de logs
criar_diretorio_logs() {
    if [ ! -d "$LOGS_DIR" ]; then
        mkdir "$LOGS_DIR" || { custom_log "Erro ao criar diretório de logs." ERROR; exit 1; }
        custom_log "Diretório de logs criado com sucesso." INFO
    else
        custom_log "✔ Diretório de logs já existe." INFO
    fi
}

# -------------------------------
# Funções relacionadas à validação e testes
# -------------------------------

# Função para validar a instalação
validar_instalacao() {
    custom_log "Validação da configuração..." INFO
    custom_log "Lista de pacotes instalados:" INFO
    pip list | grep -E 'whisper|torch|transformers|pytest|requests|PySide6' >> "$LOGFILE"
    custom_log "Versão do FFmpeg:" INFO
    ffmpeg -version
}

# Função para executar testes automatizados
executar_testes() {
    custom_log "Executando testes automatizados..." INFO

    for pacote in whisper torch ffmpeg-python; do
        if ! $PYTHON_EXEC -c "import $pacote" &> /dev/null; then
            custom_log "Erro: O pacote $pacote não está funcionando corretamente." ERROR
            exit 1
        fi
    done

    custom_log "✔ Todas as dependências foram testadas com sucesso." INFO
}

# Validar instalação das dependências
validate_python_packages

# Testar funcionalidade do pip
custom_log "Testando funcionalidade do pip..." INFO
required_pip_version="22.0"
installed_pip_version=$(pip --version | awk '{print $2}')
if [[ $(echo -e "$required_pip_version\n$installed_pip_version" | sort -V | head -n1) != "$required_pip_version" ]]; then
    custom_log "Erro: pip $required_pip_version ou superior é necessário. Versão atual: $installed_pip_version" ERROR
    exit 1
fi
custom_log "✔ pip validado: versão $installed_pip_version." INFO

# Verificar se o pip está instalado
custom_log "Verificando a instalação global do pip..."
if ! command -v pip &> /dev/null; then
    custom_log "Erro: pip não está instalado globalmente. Tentando instalar pip..." ERROR
    $PYTHON_EXEC -m ensurepip --upgrade || {
        custom_log "Erro ao instalar o pip globalmente. Verifique sua instalação do Python." ERROR
        exit 1
    }
    $PYTHON_EXEC -m pip install --upgrade pip || {
        custom_log "Erro ao atualizar o pip globalmente. Verifique manualmente." ERROR
        exit 1
    }
    custom_log "✔ pip instalado e atualizado globalmente."
fi

# Certificar-se de que o ambiente virtual está ativado
if [ -z "$VIRTUAL_ENV" ]; then
    custom_log "Erro: O ambiente virtual não está ativado. Por favor, ative o ambiente antes de continuar." ERROR
    exit 1
fi

# Fluxo principal do script
custom_log "Iniciando configuração do ambiente..." INFO
check_sudo
validate_system_dependencies
check_internet
criar_diretorio_logs
setup_virtualenv
instalar_dependencias
validate_python_packages
configurar_ffmpeg
executar_testes
validar_instalacao

custom_log "✔ Configuração concluída com sucesso. Ambiente pronto para uso!" INFO

if [[ "$1" == "--skip-run" ]]; then
    custom_log "Configuração concluída! O programa principal não será executado." INFO
    custom_log "Veja mais detalhes no arquivo de log: $LOGFILE" INFO
    exit 0
fi

custom_log "Executando o programa principal..." INFO
$PYTHON_EXEC main.py || custom_log "Erro ao executar o programa principal." ERROR

custom_log "Resumo da Configuração:" INFO
custom_log "✔ Ambiente virtual criado e ativado: $VENV_DIR" INFO
custom_log "✔ Dependências instaladas conforme requirements.txt" INFO
custom_log "✔ FFmpeg configurado e validado" INFO
custom_log "✔ Logs armazenados em: $LOGS_DIR" INFO
custom_log "✔ Programa principal pronto para execução" INFO
