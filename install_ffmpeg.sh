if ! ffmpeg -i /dev/null &> /dev/null; then
    log "Erro: FFmpeg não está funcionando corretamente." ERROR
    exit 1
fi
log "✔ FFmpeg testado com sucesso." INFO
