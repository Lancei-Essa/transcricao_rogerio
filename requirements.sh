if [ ! -s "requirements.txt" ]; then
    cat <<EOL > requirements.txt
PySide6==6.5.2
invoke==1.7.3
pytest==7.2.2
requests==2.31.0
transformers==4.21.0
pyannote.audio==2.1.1
loguru>=0.5.3
moviepy>=1.0.3
pydub>=0.25.1
EOL
    log "Arquivo requirements.txt criado com sucesso." INFO
else
    log "Arquivo requirements.txt já existe." INFO
fi

# Install Rust compiler
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env

# Install Xcode Command Line Tools on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    xcode-select --install
fi

# Upgrade pip, setuptools, and wheel
pip install --upgrade pip setuptools wheel

# Reinstall problematic packages
pip install --force-reinstall hmmlearn tokenizers
