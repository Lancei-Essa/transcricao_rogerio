import os

def selecionar_arquivo():
    """Abre uma janela de seleção de arquivos no macOS sem usar Tkinter."""
    script = 'osascript -e \'tell app "Finder" to set myFile to choose file\' -e \'return POSIX path of myFile\''
    arquivo = os.popen(script).read().strip()
    
    return arquivo if arquivo else None

# Teste o funcionamento chamando a função
if __name__ == "__main__":
    caminho_arquivo = selecionar_arquivo()
    print(f"Arquivo selecionado: {caminho_arquivo}" if caminho_arquivo else "Nenhum arquivo selecionado.")
