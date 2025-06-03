"""
Utilitários para o UI Inspector
Versão 1 - Com correções de serialização JSON e melhorias
"""
import os
import json
import time
import psutil
from datetime import datetime
from colorama import init, Fore, Style

# Inicializa colorama para cores no terminal
init(autoreset=True)

def print_colored(text, color=Fore.WHITE):
    """
    Imprime texto colorido no terminal
    
    Args:
        text: Texto a ser impresso
        color: Cor do Fore (colorama) para usar
    """
    print(f"{color}{text}{Style.RESET_ALL}")

def print_header(text):
    """
    Imprime cabeçalho estilizado com bordas
    
    Args:
        text: Texto do cabeçalho
    """
    print_colored("=" * 60, Fore.CYAN)
    print_colored(f" {text} ", Fore.YELLOW)
    print_colored("=" * 60, Fore.CYAN)

def print_info(text):
    """
    Imprime informação em azul com prefixo [INFO]
    
    Args:
        text: Texto informativo
    """
    print_colored(f"[INFO] {text}", Fore.BLUE)

def print_success(text):
    """
    Imprime mensagem de sucesso em verde com prefixo [SUCCESS]
    
    Args:
        text: Texto de sucesso
    """
    print_colored(f"[SUCCESS] {text}", Fore.GREEN)

def print_warning(text):
    """
    Imprime aviso em amarelo com prefixo [WARNING]
    
    Args:
        text: Texto de aviso
    """
    print_colored(f"[WARNING] {text}", Fore.YELLOW)

def print_error(text):
    """
    Imprime erro em vermelho com prefixo [ERROR]
    
    Args:
        text: Texto de erro
    """
    print_colored(f"[ERROR] {text}", Fore.RED)

def create_element_folder(element_name):
    """
    Cria pasta para salvar dados do elemento capturado
    
    Args:
        element_name: Nome do elemento para criar pasta
        
    Returns:
        str: Caminho completo da pasta criada
    """
    # Pasta base para todos os elementos capturados
    base_folder = "captured_elements"
    if not os.path.exists(base_folder):
        os.makedirs(base_folder)
    
    # Sanitiza o nome do elemento para nome de pasta válido
    # Remove caracteres especiais, mantém apenas alfanuméricos, espaços, hífens e underscores
    safe_name = "".join(c for c in element_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_name = safe_name.replace(' ', '_')
    
    # Adiciona timestamp para evitar conflitos de nome
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"{safe_name}_{timestamp}"
    
    # Cria a pasta do elemento
    element_folder = os.path.join(base_folder, folder_name)
    os.makedirs(element_folder, exist_ok=True)
    
    return element_folder

def save_element_data(folder_path, element_data):
    """
    Salva dados do elemento em JSON preservando estrutura complexa
    
    Esta função foi corrigida para preservar estruturas de dados complexas
    como dicionários e listas aninhadas, ao invés de converter tudo para string.
    
    Args:
        folder_path: Caminho da pasta onde salvar o arquivo
        element_data: Dicionário com dados do elemento
        
    Returns:
        str: Caminho completo do arquivo salvo
    """
    file_path = os.path.join(folder_path, "element_data.json")
    
    def make_serializable(obj):
        """
        Converte objetos para formato serializável preservando estrutura
        
        Args:
            obj: Objeto a ser convertido
            
        Returns:
            Objeto em formato serializável para JSON
        """
        if obj is None:
            return None
        elif isinstance(obj, (str, int, bool, float)):
            # Tipos primitivos já são serializáveis
            return obj
        elif isinstance(obj, dict):
            # Preserva estrutura de dicionários
            return {k: make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            # Preserva estrutura de listas
            return [make_serializable(item) for item in obj]
        elif isinstance(obj, tuple):
            # Converte tuplas para listas (JSON não suporta tuplas)
            return list(obj)
        elif hasattr(obj, '_asdict'):
            # Para namedtuples do psutil
            return make_serializable(obj._asdict())
        else:
            # Para outros objetos, converte para string como fallback
            return str(obj)
    
    # Converte dados recursivamente preservando estrutura
    serializable_data = make_serializable(element_data)
    
    # Adiciona timestamp da captura
    serializable_data['captured_at'] = datetime.now().isoformat()
    
    # Salva em arquivo JSON com formatação legível
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(serializable_data, f, indent=2, ensure_ascii=False)
    
    return file_path

def get_process_info(process_id):
    """
    Obtém informações detalhadas do processo
    
    Args:
        process_id: ID do processo Windows
        
    Returns:
        dict: Informações do processo ou erro se não acessível
    """
    try:
        # Obtém objeto do processo
        process = psutil.Process(process_id)
        
        # Coleta informações do processo
        return {
            'name': process.name(),
            'exe': process.exe(),
            'cmdline': ' '.join(process.cmdline()) if process.cmdline() else '',
            'create_time': datetime.fromtimestamp(process.create_time()).isoformat(),
            'memory_info': process.memory_info()._asdict()  # Será convertido pela serialização
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        # Retorna informações de erro quando processo não é acessível
        return {
            'name': 'Unknown',
            'exe': 'Unknown',
            'error': 'Process access denied or not found'
        }

def wait_for_keypress(message="Pressione ENTER para continuar..."):
    """
    Aguarda o usuário pressionar ENTER
    
    Args:
        message: Mensagem a exibir (padrão: "Pressione ENTER para continuar...")
    """
    print_colored(message, Fore.CYAN)
    input()