"""
UI Inspector - Inspetor de Elementos para Programas Desktop Windows
Versão 2 - Com suporte para captura de elemento âncora + clique relativo

Desenvolvido para automação RPA com UIA3

Uso:
    python main.py

Controles durante captura:
    CTRL + Click - Capturar elemento sob o cursor
    CTRL + SHIFT + Click - Capturar elemento âncora (para clique relativo)
    ESC - Cancelar captura
"""
import sys
import os
import json
import time
from element_inspector import ElementInspector
from utils import *

class UIInspectorApp:
    """
    Aplicação principal do UI Inspector
    
    Gerencia a interface de usuário e coordena as operações
    de captura e visualização de elementos.
    """
    
    def __init__(self):
        """Inicializa a aplicação com o inspector de elementos"""
        self.inspector = ElementInspector()
        self.running = True
    
    def show_banner(self):
        """
        Exibe banner da aplicação
        
        Banner com título e informações sobre a ferramenta
        """
        print_colored("=" * 70, Fore.CYAN)
        print_colored("                    UI INSPECTOR v3.0", Fore.YELLOW)
        print_colored("              Inspetor de Elementos Windows Desktop", Fore.WHITE)
        print_colored("                🎯 COM SELETORES ULTRA-ROBUSTOS 🎯", Fore.GREEN)
        print_colored("                    Powered by UIA3", Fore.GREEN)
        print_colored("=" * 70, Fore.CYAN)
        print()
    
    def show_main_menu(self):
        """
        Exibe menu principal
        
        Mostra todas as opções disponíveis para o usuário
        """
        print_header("MENU PRINCIPAL")
        print_colored("1. Capturar Elemento", Fore.WHITE)
        print_colored("2. Capturar Elemento Âncora + Clique Relativo", Fore.WHITE)
        print_colored("3. Listar Elementos Capturados", Fore.WHITE)
        print_colored("4. Testar Seletor XML", Fore.CYAN)
        print_colored("5. Abrir Pasta de Elementos", Fore.WHITE)
        print_colored("6. Ajuda", Fore.WHITE)
        print_colored("7. Sair", Fore.WHITE)
        print()
    
    def get_user_choice(self):
        """
        Obtém escolha do usuário
        
        Trata interrupções do teclado graciosamente
        
        Returns:
            str: Escolha do usuário ou "6" para sair
        """
        try:
            choice = input(f"{Fore.CYAN}Escolha uma opção (1-7): {Style.RESET_ALL}").strip()
            return choice
        except KeyboardInterrupt:
            return "7"
        except:
            return ""
    
    def capture_element_workflow(self):
        """
        Fluxo completo de captura de elemento
        
        Guia o usuário através do processo de captura,
        desde a nomeação até a visualização dos detalhes.
        """
        print_header("CAPTURA DE ELEMENTO")
        
        # Solicita nome do elemento
        element_name = input(f"{Fore.CYAN}Digite um nome para o elemento: {Style.RESET_ALL}").strip()
        
        if not element_name:
            print_error("Nome do elemento é obrigatório")
            wait_for_keypress()
            return
        
        print()
        print_warning("INSTRUÇÕES:")
        print_colored("• CTRL + Click no elemento para capturar", Fore.WHITE)
        print_colored("• ESC para cancelar", Fore.WHITE)
        print()
        print_colored("🎯 NOVO: Geração automática de seletores ULTRA-ROBUSTOS!", Fore.GREEN)
        print_colored("   • Análise de estabilidade de atributos", Fore.CYAN)
        print_colored("   • Múltiplas estratégias de fallback", Fore.CYAN)
        print_colored("   • Resistente a mudanças de AutomationId", Fore.CYAN)
        print()
        
        # Inicia captura imediatamente
        result = self.inspector.start_capture_mode(element_name)
        
        if result:
            print()
            print_success("Elemento capturado com sucesso!")
            
            # Oferece visualizar detalhes
            view_details = input(f"{Fore.CYAN}Deseja visualizar os detalhes? (s/n): {Style.RESET_ALL}").strip().lower()
            
            if view_details in ['s', 'sim', 'y', 'yes']:
                self.show_element_details(result['element_data'])
        else:
            print_warning("Captura cancelada ou falhou")
        
        wait_for_keypress()
    
    def capture_anchor_relative_workflow(self):
        """
        Fluxo completo de captura de elemento âncora + clique relativo
        
        Guia o usuário através do processo de captura em duas etapas:
        1. Captura do elemento âncora
        2. Marcação do ponto de clique relativo
        """
        print_header("CAPTURA DE ELEMENTO ÂNCORA + CLIQUE RELATIVO")
        
        # Explica o conceito
        print_colored("Este modo permite capturar um elemento âncora e definir", Fore.CYAN)
        print_colored("um ponto de clique relativo a ele. Isso garante que o", Fore.CYAN)
        print_colored("clique funcione independente da resolução ou tamanho da janela.", Fore.CYAN)
        print()
        
        # Solicita nome do conjunto
        element_name = input(f"{Fore.CYAN}Digite um nome para o conjunto âncora+clique: {Style.RESET_ALL}").strip()
        
        if not element_name:
            print_error("Nome é obrigatório")
            wait_for_keypress()
            return
        
        print()
        print_warning("INSTRUÇÕES:")
        print_colored("Passo 1: CTRL + SHIFT + Click no elemento âncora", Fore.WHITE)
        print_colored("Passo 2: CTRL + Click onde deseja clicar (relativo ao âncora)", Fore.WHITE)
        print_colored("ESC para cancelar a qualquer momento", Fore.WHITE)
        print()
        
        # Inicia captura com tipo anchor_relative
        result = self.inspector.start_capture_mode(element_name, capture_type="anchor_relative")
        
        if result:
            print()
            print_success("Captura âncora+clique concluída com sucesso!")
            
            # Oferece visualizar detalhes
            view_details = input(f"{Fore.CYAN}Deseja visualizar os detalhes? (s/n): {Style.RESET_ALL}").strip().lower()
            
            if view_details in ['s', 'sim', 'y', 'yes']:
                self.show_element_details(result['element_data'])
        else:
            print_warning("Captura cancelada ou falhou")
        
        wait_for_keypress()
    
    def list_captured_elements(self):
        """
        Lista elementos capturados
        
        Exibe todos os elementos salvos com preview e permite
        visualizar detalhes completos de elementos específicos.
        """
        print_header("ELEMENTOS CAPTURADOS")
        
        base_folder = "captured_elements"
        
        if not os.path.exists(base_folder):
            print_warning("Nenhum elemento capturado ainda")
            wait_for_keypress()
            return
        
        try:
            # Lista apenas diretórios (cada elemento fica em uma pasta)
            elements = os.listdir(base_folder)
            elements = [d for d in elements if os.path.isdir(os.path.join(base_folder, d))]
            
            if not elements:
                print_warning("Nenhum elemento capturado ainda")
            else:
                print_info(f"Total de elementos capturados: {len(elements)}")
                print()
                
                # Mostra lista numerada dos elementos
                for i, element_folder in enumerate(sorted(elements), 1):
                    print_colored(f"{i:2d}. {element_folder}", Fore.CYAN)
                    
                    # Tenta carregar informações básicas para prévia
                    try:
                        file_path = os.path.join(base_folder, element_folder, "element_data.json")
                        if os.path.exists(file_path):
                            with open(file_path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                            
                            # Extrai informações para preview
                            capture_type = data.get('capture_type', 'single_element')
                            captured_at = data.get('captured_at', 'N/A')
                            
                            # Formata timestamp para exibição
                            if captured_at != 'N/A':
                                captured_at = captured_at[:19]  # Remove milissegundos
                            
                            if capture_type == 'anchor_relative':
                                # Para captura âncora+clique
                                anchor = data.get('anchor_element', {})
                                anchor_name = anchor.get('name', 'N/A')
                                anchor_type = anchor.get('control_type', 'N/A')
                                print_colored(f"    [ÂNCORA+CLIQUE] {anchor_name} ({anchor_type}) - {captured_at}", Fore.MAGENTA)
                            else:
                                # Para captura simples
                                name = data.get('name', 'N/A')
                                control_type = data.get('control_type', 'N/A')
                                print_colored(f"    {name} ({control_type}) - {captured_at}", Fore.WHITE)
                    except Exception:
                        print_colored(f"    Erro ao ler preview", Fore.RED)
                    print()
                
                # Opções de visualização
                print_colored("Opções:", Fore.YELLOW)
                print_colored("• Digite o número do elemento para ver DETALHES COMPLETOS", Fore.WHITE)
                print_colored("• Digite 'todos' para ver TODOS os elementos em detalhes", Fore.WHITE)
                print_colored("• ENTER para voltar ao menu", Fore.WHITE)
                print()
                
                choice = input(f"{Fore.CYAN}Sua escolha: {Style.RESET_ALL}").strip().lower()
                
                if choice == 'todos':
                    # Mostra todos os elementos em detalhes
                    for i, element_folder in enumerate(sorted(elements), 1):
                        print()
                        print_colored("=" * 70, Fore.MAGENTA)
                        print_colored(f"ELEMENTO {i}: {element_folder}", Fore.YELLOW)
                        print_colored("=" * 70, Fore.MAGENTA)
                        self.show_saved_element_details(element_folder)
                        
                        if i < len(elements):  # Não pergunta no último elemento
                            continue_viewing = input(f"{Fore.CYAN}Continuar para próximo elemento? (s/n): {Style.RESET_ALL}").strip().lower()
                            if continue_viewing not in ['s', 'sim', 'y', 'yes', '']:
                                break
                
                elif choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(elements):
                        element_folder = sorted(elements)[idx]
                        print()
                        print_colored("=" * 70, Fore.MAGENTA)
                        print_colored(f"ELEMENTO SELECIONADO: {element_folder}", Fore.YELLOW)
                        print_colored("=" * 70, Fore.MAGENTA)
                        self.show_saved_element_details(element_folder)
                    else:
                        print_error("Número inválido")
        
        except Exception as e:
            print_error(f"Erro ao listar elementos: {str(e)}")
        
        wait_for_keypress()
    
    def show_element_details(self, element_data):
        """
        Exibe detalhes completos do elemento
        
        Função unificada para exibir detalhes tanto de elementos
        recém-capturados quanto de elementos salvos.
        
        Args:
            element_data: Dicionário com dados do elemento
        """
        print_header("DETALHES DO ELEMENTO")
        
        # Função auxiliar para acessar dados de forma segura
        def safe_get(data, key, default='N/A'):
            """Obtém valor de forma segura de um dicionário"""
            if isinstance(data, dict):
                return data.get(key, default)
            return default
        
        # PROPRIEDADES PRINCIPAIS
        print_colored("PROPRIEDADES PRINCIPAIS:", Fore.YELLOW)
        print_colored(f"  AutomationId: {safe_get(element_data, 'automation_id')}", Fore.WHITE)
        print_colored(f"  Name: {safe_get(element_data, 'name')}", Fore.WHITE)
        print_colored(f"  ClassName: {safe_get(element_data, 'class_name')}", Fore.WHITE)
        print_colored(f"  ControlType: {safe_get(element_data, 'control_type')}", Fore.WHITE)
        print_colored(f"  LocalizedControlType: {safe_get(element_data, 'localized_control_type')}", Fore.WHITE)
        print_colored(f"  FrameworkId: {safe_get(element_data, 'framework_id')}", Fore.WHITE)
        print_colored(f"  FrameworkType: {safe_get(element_data, 'framework_type')}", Fore.WHITE)
        print_colored(f"  ProcessId: {safe_get(element_data, 'process_id')}", Fore.WHITE)
        print()
        
        # INFORMAÇÕES DA JANELA
        window_info = element_data.get('window_info', {}) if isinstance(element_data, dict) else {}
        if isinstance(window_info, dict) and window_info and not window_info.get('error'):
            print_colored("JANELA:", Fore.YELLOW)
            print_colored(f"  Título: {safe_get(window_info, 'title')}", Fore.WHITE)
            print_colored(f"  Classe: {safe_get(window_info, 'class_name')}", Fore.WHITE)
            print_colored(f"  AutomationId: {safe_get(window_info, 'automation_id')}", Fore.WHITE)
            print_colored(f"  ProcessId: {safe_get(window_info, 'process_id')}", Fore.WHITE)
            
            # Propriedades especiais da janela
            if window_info.get('is_modal') is not None:
                print_colored(f"  Modal: {window_info.get('is_modal')}", Fore.WHITE)
            if window_info.get('is_topmost') is not None:
                print_colored(f"  Topmost: {window_info.get('is_topmost')}", Fore.WHITE)
            print()
        
        # DETECÇÃO DE JANELA DE DESTINO
        target_window = element_data.get('target_window_detection', {}) if isinstance(element_data, dict) else {}
        if isinstance(target_window, dict) and target_window.get('likely_opens_window'):
            print_colored("DETECÇÃO DE JANELA DE DESTINO:", Fore.YELLOW)
            print_colored(f"  Provável abertura de janela: SIM", Fore.GREEN)
            print_colored(f"  Tipo de controle: {safe_get(target_window, 'control_type')}", Fore.WHITE)
            print_colored(f"  Texto do botão: {safe_get(target_window, 'button_text')}", Fore.WHITE)
            
            hints = target_window.get('detection_hints', [])
            if hints:
                print_colored("  Dicas:", Fore.CYAN)
                for hint in hints:
                    print_colored(f"    • {hint}", Fore.WHITE)
            print()
        
        # ESTADOS
        print_colored("ESTADOS:", Fore.YELLOW)
        print_colored(f"  Habilitado: {safe_get(element_data, 'is_enabled')}", Fore.WHITE)
        print_colored(f"  Visível: {safe_get(element_data, 'is_visible')}", Fore.WHITE)
        print_colored(f"  Focalizável: {safe_get(element_data, 'is_keyboard_focusable')}", Fore.WHITE)
        print_colored(f"  Tem foco: {safe_get(element_data, 'has_keyboard_focus')}", Fore.WHITE)
        print_colored(f"  É elemento de conteúdo: {safe_get(element_data, 'is_content_element')}", Fore.WHITE)
        print_colored(f"  É elemento de controle: {safe_get(element_data, 'is_control_element')}", Fore.WHITE)
        print()
        
        # GEOMETRIA
        rect = element_data.get('bounding_rectangle', {}) if isinstance(element_data, dict) else {}
        if isinstance(rect, dict) and rect:
            print_colored("GEOMETRIA:", Fore.YELLOW)
            print_colored(f"  Posição: ({safe_get(rect, 'left')}, {safe_get(rect, 'top')})", Fore.WHITE)
            print_colored(f"  Tamanho: {safe_get(rect, 'width')} x {safe_get(rect, 'height')}", Fore.WHITE)
            print_colored(f"  Retângulo: L={safe_get(rect, 'left')}, T={safe_get(rect, 'top')}, R={safe_get(rect, 'right')}, B={safe_get(rect, 'bottom')}", Fore.WHITE)
            print()
        
        # VALOR DO ELEMENTO
        value = safe_get(element_data, 'value')
        if value and value != 'N/A':
            print_colored("VALOR:", Fore.YELLOW)
            print_colored(f"  {value}", Fore.WHITE)
            print()
        
        # INFORMAÇÕES DO PAI
        parent_info = element_data.get('parent_info', {}) if isinstance(element_data, dict) else {}
        if isinstance(parent_info, dict) and parent_info:
            print_colored("ELEMENTO PAI:", Fore.YELLOW)
            print_colored(f"  AutomationId: {safe_get(parent_info, 'automation_id')}", Fore.WHITE)
            print_colored(f"  Name: {safe_get(parent_info, 'name')}", Fore.WHITE)
            print_colored(f"  ClassName: {safe_get(parent_info, 'class_name')}", Fore.WHITE)
            print_colored(f"  ControlType: {safe_get(parent_info, 'control_type')}", Fore.WHITE)
            print()
        
        # NÚMERO DE FILHOS
        children_count = safe_get(element_data, 'children_count')
        if children_count is not None and children_count != 'N/A':
            print_colored("HIERARQUIA:", Fore.YELLOW)
            print_colored(f"  Número de elementos filhos: {children_count}", Fore.WHITE)
            print()
        
        # PADRÕES SUPORTADOS
        patterns = element_data.get('supported_patterns', {}) if isinstance(element_data, dict) else {}
        if isinstance(patterns, dict):
            supported_patterns = []
            for name, info in patterns.items():
                if info and info != False and info != 'False':
                    if isinstance(info, dict) and info.get('supported'):
                        # Extrai informações adicionais do padrão
                        extra_info = []
                        
                        # ValuePattern
                        if info.get('value') is not None:
                            extra_info.append(f"valor='{info['value']}'")
                        if info.get('is_read_only') is not None:
                            extra_info.append(f"readonly={info['is_read_only']}")
                        
                        # TogglePattern
                        if info.get('toggle_state') is not None:
                            extra_info.append(f"estado={info['toggle_state']}")
                        
                        # RangeValuePattern
                        if info.get('minimum') is not None:
                            extra_info.append(f"min={info['minimum']}")
                        if info.get('maximum') is not None:
                            extra_info.append(f"max={info['maximum']}")
                        
                        # ExpandCollapsePattern
                        if info.get('expand_collapse_state') is not None:
                            extra_info.append(f"estado={info['expand_collapse_state']}")
                        
                        # ScrollPattern
                        if info.get('horizontal_scroll_percent') is not None:
                            extra_info.append(f"h_scroll={info['horizontal_scroll_percent']}%")
                        if info.get('vertical_scroll_percent') is not None:
                            extra_info.append(f"v_scroll={info['vertical_scroll_percent']}%")
                        
                        # SelectionPattern
                        if info.get('can_select_multiple') is not None:
                            extra_info.append(f"multi_select={info['can_select_multiple']}")
                        
                        # WindowPattern
                        if info.get('can_maximize') is not None:
                            extra_info.append(f"maximizable={info['can_maximize']}")
                        if info.get('can_minimize') is not None:
                            extra_info.append(f"minimizable={info['can_minimize']}")
                        
                        extra_str = f" ({', '.join(extra_info)})" if extra_info else ""
                        supported_patterns.append(f"{name}{extra_str}")
                    else:
                        supported_patterns.append(name)
            
            if supported_patterns:
                print_colored("PADRÕES SUPORTADOS:", Fore.YELLOW)
                for pattern in supported_patterns:
                    print_colored(f"  • {pattern}", Fore.WHITE)
                print()
        
        # INFORMAÇÕES DO PROCESSO
        process_info = element_data.get('process_info', {}) if isinstance(element_data, dict) else {}
        if isinstance(process_info, dict) and process_info and not process_info.get('error'):
            print_colored("PROCESSO:", Fore.YELLOW)
            print_colored(f"  Nome: {safe_get(process_info, 'name')}", Fore.WHITE)
            print_colored(f"  Executável: {safe_get(process_info, 'exe')}", Fore.WHITE)
            
            # Linha de comando se disponível
            cmdline = safe_get(process_info, 'cmdline')
            if cmdline and cmdline != 'N/A':
                print_colored(f"  Linha de comando: {cmdline}", Fore.WHITE)
            
            # Tempo de criação
            create_time = safe_get(process_info, 'create_time')
            if create_time and create_time != 'N/A':
                print_colored(f"  Iniciado em: {create_time}", Fore.WHITE)
            
            # Informações de memória
            memory_info = process_info.get('memory_info', {})
            if isinstance(memory_info, dict) and memory_info:
                rss = memory_info.get('rss', 0)
                if rss > 0:
                    # Converte bytes para MB
                    rss_mb = rss / (1024 * 1024)
                    print_colored(f"  Memória em uso: {rss_mb:.1f} MB", Fore.WHITE)
            print()
        
        # RUNTIME ID
        runtime_id = element_data.get('runtime_id', []) if isinstance(element_data, dict) else []
        if runtime_id and isinstance(runtime_id, list) and len(runtime_id) > 0:
            print_colored("RUNTIME ID:", Fore.YELLOW)
            print_colored(f"  {runtime_id}", Fore.WHITE)
            print()
        
        # SELETORES XML
        selectors = element_data.get('xml_selectors', []) if isinstance(element_data, dict) else []
        if isinstance(selectors, list) and selectors:
            print_colored("SELETORES XML:", Fore.YELLOW)
            
            # Mostra até 5 seletores
            for i, selector in enumerate(selectors[:5], 1):
                print_colored(f"\n  Seletor {i}:", Fore.CYAN)
                if isinstance(selector, str):
                    # Indenta o XML para melhor visualização
                    lines = selector.strip().split('\n')
                    for line in lines:
                        print_colored(f"    {line}", Fore.WHITE)
                else:
                    print_colored(f"    {str(selector)}", Fore.WHITE)
            
            if len(selectors) > 5:
                print_colored(f"\n  ... e mais {len(selectors) - 5} seletores", Fore.YELLOW)
            print()
        
        # TIMESTAMP DE CAPTURA
        captured_at = safe_get(element_data, 'captured_at')
        if captured_at and captured_at != 'N/A':
            print_colored("CAPTURA:", Fore.YELLOW)
            print_colored(f"  Data/Hora: {captured_at}", Fore.WHITE)
            print()
        
        # INFORMAÇÕES DE CLIQUE RELATIVO (se for captura âncora+clique)
        if safe_get(element_data, 'capture_type') == 'anchor_relative':
            print_colored("=" * 60, Fore.MAGENTA)
            print_colored("INFORMAÇÕES DE CLIQUE RELATIVO", Fore.YELLOW)
            print_colored("=" * 60, Fore.MAGENTA)
            
            # Informações do elemento âncora
            anchor = element_data.get('anchor_element', {})
            if isinstance(anchor, dict):
                print_colored("\nELEMENTO ÂNCORA:", Fore.YELLOW)
                print_colored(f"  AutomationId: {safe_get(anchor, 'automation_id')}", Fore.CYAN)
                print_colored(f"  Name: {safe_get(anchor, 'name')}", Fore.CYAN)
                print_colored(f"  ClassName: {safe_get(anchor, 'class_name')}", Fore.CYAN)
                print_colored(f"  ControlType: {safe_get(anchor, 'control_type')}", Fore.CYAN)
                
                # Geometria do âncora
                anchor_rect = anchor.get('bounding_rectangle', {})
                if isinstance(anchor_rect, dict) and anchor_rect:
                    print_colored(f"  Posição: ({safe_get(anchor_rect, 'left')}, {safe_get(anchor_rect, 'top')})", Fore.WHITE)
                    print_colored(f"  Tamanho: {safe_get(anchor_rect, 'width')} x {safe_get(anchor_rect, 'height')}", Fore.WHITE)
            
            # Informações do clique relativo
            relative_click = element_data.get('relative_click', {})
            if isinstance(relative_click, dict):
                print_colored("\nCLIQUE RELATIVO:", Fore.YELLOW)
                
                # Posição absoluta
                abs_pos = relative_click.get('absolute_position', {})
                if isinstance(abs_pos, dict):
                    print_colored(f"  Posição absoluta: ({safe_get(abs_pos, 'x')}, {safe_get(abs_pos, 'y')})", Fore.WHITE)
                
                # Offset do âncora
                anchor_rel = relative_click.get('anchor_relative', {})
                if isinstance(anchor_rel, dict):
                    print_colored(f"\n  Relativo ao âncora:", Fore.GREEN)
                    print_colored(f"    Offset X: {safe_get(anchor_rel, 'offset_x')}px", Fore.WHITE)
                    print_colored(f"    Offset Y: {safe_get(anchor_rel, 'offset_y')}px", Fore.WHITE)
                    desc = safe_get(anchor_rel, 'description')
                    if desc and desc != 'N/A':
                        print_colored(f"    Descrição: {desc}", Fore.WHITE)
                
                # Offset da janela
                window_rel = relative_click.get('window_relative', {})
                if isinstance(window_rel, dict):
                    print_colored(f"\n  Relativo à janela:", Fore.GREEN)
                    print_colored(f"    Offset X: {safe_get(window_rel, 'offset_x')}px", Fore.WHITE)
                    print_colored(f"    Offset Y: {safe_get(window_rel, 'offset_y')}px", Fore.WHITE)
                    print_colored(f"    Percentual X: {safe_get(window_rel, 'percent_x')}%", Fore.WHITE)
                    print_colored(f"    Percentual Y: {safe_get(window_rel, 'percent_y')}%", Fore.WHITE)
                    desc = safe_get(window_rel, 'description')
                    if desc and desc != 'N/A':
                        print_colored(f"    Descrição: {desc}", Fore.WHITE)
            
            # Contexto da janela
            window_ctx = element_data.get('window_context', {})
            if isinstance(window_ctx, dict):
                print_colored("\nCONTEXTO DA JANELA:", Fore.YELLOW)
                print_colored(f"  Título: {safe_get(window_ctx, 'title')}", Fore.WHITE)
                print_colored(f"  Classe: {safe_get(window_ctx, 'class_name')}", Fore.WHITE)
                print_colored(f"  Tamanho: {safe_get(window_ctx, 'width')} x {safe_get(window_ctx, 'height')} pixels", Fore.WHITE)
            
            print()  # Linha em branco após seção de clique relativo
    
    def show_saved_element_details(self, element_folder):
        """
        Exibe detalhes de um elemento salvo
        
        Carrega o arquivo JSON e usa a mesma função de exibição
        para garantir consistência.
        
        Args:
            element_folder: Nome da pasta do elemento
        """
        try:
            file_path = os.path.join("captured_elements", element_folder, "element_data.json")
            
            if not os.path.exists(file_path):
                print_error("Arquivo de dados não encontrado")
                return
            
            # Carrega dados do arquivo JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                element_data = json.load(f)
            
            # Usa a mesma função de exibição
            self.show_element_details(element_data)
            
        except Exception as e:
            print_error(f"Erro ao carregar elemento: {str(e)}")
    
    def test_xml_selector_workflow(self):
        """
        Fluxo completo de teste de seletor XML
        
        Permite ao usuário inserir um seletor XML e testa sua funcionalidade
        """
        print_header("TESTE DE SELETOR XML")
        
        print_colored("SOBRE O TESTE DE SELETORES:", Fore.YELLOW)
        print_colored("• Valida sintaxe XML do seletor", Fore.WHITE)
        print_colored("• Testa se consegue encontrar o elemento", Fore.WHITE)
        print_colored("• Avalia confiabilidade com múltiplas execuções", Fore.WHITE)
        print_colored("• Mede tempo de execução", Fore.WHITE)
        print()
        
        print_colored("FORMATO DO SELETOR XML:", Fore.YELLOW)
        print_colored("Exemplo básico:", Fore.CYAN)
        print_colored('<Selector><Window title="Calculadora" /><Element automationId="num1Button" /></Selector>', Fore.WHITE)
        print()
        
        print_colored("Cole o seletor XML para testar:", Fore.CYAN)
        print_colored("(Digite uma linha vazia para cancelar)", Fore.YELLOW)
        
        # Coleta entrada do usuário (pode ser multilinha)
        xml_lines = []
        while True:
            try:
                line = input().strip()
                if not line:
                    if not xml_lines:
                        print_warning("Teste cancelado")
                        wait_for_keypress()
                        return
                    else:
                        break
                xml_lines.append(line)
            except KeyboardInterrupt:
                print_warning("Teste cancelado")
                wait_for_keypress()
                return
        
        xml_selector = ' '.join(xml_lines).strip()
        
        if not xml_selector:
            print_error("Seletor XML vazio")
            wait_for_keypress()
            return
        
        print()
        print_info("Testando seletor XML...")
        print_colored(f"Seletor: {xml_selector}", Fore.MAGENTA)
        print()
        
        try:
            # Executa teste usando o inspector
            test_result = self.inspector.test_xml_selector(xml_selector)
            
            # Exibe resultado
            print_header("RESULTADO DO TESTE")
            
            if test_result['success']:
                print_success("✓ SELETOR VÁLIDO!")
                
                reliability = test_result.get('reliability', {})
                if reliability:
                    print_colored(f"Confiabilidade: {reliability['reliability_percentage']:.1f}%", Fore.GREEN)
                    print_colored(f"Classificação: {reliability['classification']}", Fore.GREEN)
                    print_colored(f"Tempo médio: {reliability['average_execution_time']:.3f}s", Fore.CYAN)
                    print_colored(f"Execuções bem-sucedidas: {reliability['successful_executions']}/{reliability['total_executions']}", Fore.CYAN)
                
                validation = test_result.get('validation', {})
                if validation:
                    print_colored(f"Tempo de validação: {validation['validation_time']:.3f}s", Fore.CYAN)
                
                print()
                print_colored("RECOMENDAÇÕES:", Fore.YELLOW)
                
                reliability_pct = reliability.get('reliability_percentage', 0)
                if reliability_pct >= 90:
                    print_colored("• Excelente seletor - recomendado para produção", Fore.GREEN)
                elif reliability_pct >= 75:
                    print_colored("• Bom seletor - adequado para a maioria dos casos", Fore.GREEN)
                elif reliability_pct >= 50:
                    print_colored("• Seletor moderado - considere usar como fallback", Fore.YELLOW)
                else:
                    print_colored("• Seletor instável - não recomendado para produção", Fore.RED)
                    print_colored("• Considere capturar o elemento novamente", Fore.RED)
                
                # NOVA FUNCIONALIDADE: Opções de ação
                print()
                print_colored("OPÇÕES DE AÇÃO:", Fore.YELLOW)
                print_colored("1. Executar CLIQUE no elemento", Fore.WHITE)
                print_colored("2. Executar CLIQUE DUPLO no elemento", Fore.WHITE)
                print_colored("3. Executar CLIQUE DIREITO no elemento", Fore.WHITE)
                print_colored("4. Apenas testar (não executar ação)", Fore.WHITE)
                print()
                
                action_choice = input(f"{Fore.CYAN}Escolha uma ação (1-4): {Style.RESET_ALL}").strip()
                
                if action_choice == "1":
                    self._execute_selector_action(xml_selector, "click")
                elif action_choice == "2":
                    self._execute_selector_action(xml_selector, "double_click")
                elif action_choice == "3":
                    self._execute_selector_action(xml_selector, "right_click")
                elif action_choice == "4":
                    print_info("Teste concluído sem execução de ação")
                else:
                    print_warning("Opção inválida - apenas testando seletor")
                
            else:
                print_error("✗ SELETOR INVÁLIDO!")
                print_colored(f"Erro: {test_result.get('message', 'Erro desconhecido')}", Fore.RED)
                
                validation = test_result.get('validation', {})
                if validation and validation.get('errors'):
                    print()
                    print_colored("DETALHES DO ERRO:", Fore.YELLOW)
                    for error in validation['errors']:
                        print_colored(f"• {error}", Fore.RED)
                
                print()
                print_colored("DICAS PARA CORREÇÃO:", Fore.YELLOW)
                print_colored("• Verifique se a janela/aplicação está aberta", Fore.WHITE)
                print_colored("• Confirme se os atributos estão corretos", Fore.WHITE)
                print_colored("• Tente um seletor mais genérico", Fore.WHITE)
                print_colored("• Capture o elemento novamente", Fore.WHITE)
        
        except Exception as e:
            print_error(f"Erro durante teste: {str(e)}")
        
        wait_for_keypress()
    
    def _execute_selector_action(self, xml_selector, action_type):
        """
        Executa ação específica no elemento encontrado pelo seletor
        
        Args:
            xml_selector (str): Seletor XML
            action_type (str): Tipo de ação a executar
        """
        print()
        print_warning(f"EXECUTANDO {action_type.upper().replace('_', ' ')}...")
        print_colored("⚠️  Esta ação será executada IMEDIATAMENTE!", Fore.YELLOW)
        print_colored("⚠️  Certifique-se de que a janela/aplicação está na posição correta!", Fore.YELLOW)
        
        confirm = input(f"{Fore.CYAN}Confirma execução? (s/n): {Style.RESET_ALL}").strip().lower()
        
        if confirm not in ['s', 'sim', 'y', 'yes']:
            print_info("Execução cancelada pelo usuário")
            return
        
        print()
        print_info("Aguarde 3 segundos para execução...")
        for i in range(3, 0, -1):
            print_colored(f"{i}...", Fore.YELLOW)
            time.sleep(1)
        
        print()
        try:
            # Executa a ação
            action_result = self.inspector.execute_xml_selector_action(xml_selector, action_type)
            
            if action_result['success']:
                print()
                print_success(f"✓ {action_type.upper().replace('_', ' ')} EXECUTADO COM SUCESSO!")
                print_colored(f"💡 {action_result.get('message', 'Ação concluída')}", Fore.GREEN)
                
                if 'execution_time' in action_result:
                    print_colored(f"⏱️  Tempo de execução: {action_result['execution_time']:.3f}s", Fore.CYAN)
                    
            else:
                print()
                print_error(f"✗ FALHA AO EXECUTAR {action_type.upper().replace('_', ' ')}:")
                print_colored(f"❌ {action_result.get('error', 'Erro desconhecido')}", Fore.RED)
                
                print()
                print_colored("POSSÍVEIS CAUSAS:", Fore.YELLOW)
                print_colored("• Elemento não encontrado", Fore.WHITE)
                print_colored("• Janela/aplicação foi fechada", Fore.WHITE)
                print_colored("• Elemento não suporta a ação solicitada", Fore.WHITE)
                print_colored("• Permissions ou segurança bloquearam a ação", Fore.WHITE)
                
        except Exception as e:
            print_error(f"Erro durante execução de ação: {str(e)}")
    
    def open_elements_folder(self):
        """
        Abre pasta de elementos capturados
        
        Funciona em Windows, macOS e Linux
        """
        import subprocess
        import platform
        
        folder_path = os.path.abspath("captured_elements")
        
        # Cria a pasta se não existir
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        try:
            if platform.system() == "Windows":
                os.startfile(folder_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", folder_path])
            else:  # Linux
                subprocess.run(["xdg-open", folder_path])
            
            print_success(f"Pasta aberta: {folder_path}")
            
        except Exception as e:
            print_error(f"Erro ao abrir pasta: {str(e)}")
            print_info(f"Caminho da pasta: {folder_path}")
        
        wait_for_keypress()
    
    def show_help(self):
        """
        Exibe ajuda detalhada sobre o uso da aplicação
        """
        print_header("AJUDA - UI INSPECTOR")
        
        print_colored("SOBRE:", Fore.YELLOW)
        print_colored("  O UI Inspector é uma ferramenta profissional para capturar", Fore.WHITE)
        print_colored("  informações detalhadas de elementos de interface em programas", Fore.WHITE)
        print_colored("  Windows, projetada para automação RPA com UIA3.", Fore.WHITE)
        print()
        
        print_colored("MODOS DE CAPTURA:", Fore.YELLOW)
        print_colored("  1. CAPTURA SIMPLES:", Fore.CYAN)
        print_colored("     • Captura informações de um único elemento", Fore.WHITE)
        print_colored("     • Use: CTRL + Click no elemento", Fore.WHITE)
        print_colored("  2. CAPTURA ÂNCORA + CLIQUE RELATIVO:", Fore.CYAN)
        print_colored("     • Captura elemento âncora e define ponto de clique relativo", Fore.WHITE)
        print_colored("     • Garante cliques precisos independente de resolução", Fore.WHITE)
        print_colored("     • Passo 1: CTRL + SHIFT + Click no elemento âncora", Fore.WHITE)
        print_colored("     • Passo 2: CTRL + Click onde deseja clicar", Fore.WHITE)
        print()
        
        print_colored("COMO USAR:", Fore.YELLOW)
        print_colored("  1. Escolha o modo de captura desejado no menu", Fore.WHITE)
        print_colored("  2. Digite um nome descritivo para identificar", Fore.WHITE)
        print_colored("  3. Siga as instruções na tela para capturar", Fore.WHITE)
        print_colored("  4. Visualize os detalhes capturados", Fore.WHITE)
        print()
        
        print_colored("LISTAGEM DE ELEMENTOS:", Fore.YELLOW)
        print_colored("  • Lista todos os elementos capturados com preview", Fore.WHITE)
        print_colored("  • Digite o número para ver detalhes COMPLETOS", Fore.WHITE)
        print_colored("  • Digite 'todos' para ver TODOS em sequência", Fore.WHITE)
        print_colored("  • Mostra tanto capturas simples quanto âncora+clique", Fore.WHITE)
        print()
        
        print_colored("INFORMAÇÕES CAPTURADAS:", Fore.YELLOW)
        print_colored("  CAPTURA SIMPLES:", Fore.CYAN)
        print_colored("    • Identificação: AutomationId, Name, ClassName", Fore.WHITE)
        print_colored("    • Tipo: ControlType, LocalizedControlType", Fore.WHITE)
        print_colored("    • Framework: FrameworkId, FrameworkType detectado", Fore.WHITE)
        print_colored("    • Processo: ProcessId, nome, executável, memória", Fore.WHITE)
        print_colored("    • Janela: Título, classe, se é modal/topmost", Fore.WHITE)
        print_colored("    • Geometria: Posição e tamanho exatos", Fore.WHITE)
        print_colored("    • Estados: Habilitado, visível, focalizável", Fore.WHITE)
        print_colored("    • Hierarquia: Informações do pai e número de filhos", Fore.WHITE)
        print_colored("    • Padrões: Todos os padrões UIA suportados", Fore.WHITE)
        print_colored("    • Seletores: Múltiplos seletores XML executáveis e validados", Fore.WHITE)
        print_colored("    • Validação: Seletores testados automaticamente", Fore.WHITE)
        print_colored("    • Detecção: Identifica elementos que abrem janelas", Fore.WHITE)
        print_colored("  CAPTURA ÂNCORA+CLIQUE:", Fore.CYAN)
        print_colored("    • Todas as informações do elemento âncora", Fore.WHITE)
        print_colored("    • Offset em pixels do âncora", Fore.WHITE)
        print_colored("    • Offset em pixels da janela", Fore.WHITE)
        print_colored("    • Percentual da janela (independente de resolução)", Fore.WHITE)
        print_colored("    • Contexto completo da janela", Fore.WHITE)
        print_colored("    • Seletores XML especializados para clique relativo", Fore.WHITE)
        print()
        
        print_colored("CONTROLES DURANTE CAPTURA:", Fore.YELLOW)
        print_colored("  CTRL + Click         - Capturar elemento/clique", Fore.GREEN)
        print_colored("  CTRL + SHIFT + Click - Capturar elemento âncora", Fore.GREEN)
        print_colored("  ESC                  - Cancelar captura", Fore.GREEN)
        print()
        
        print_colored("TESTE DE SELETORES XML:", Fore.YELLOW)
        print_colored("  • Teste seletores XML personalizados", Fore.WHITE)
        print_colored("  • Validação automática de sintaxe", Fore.WHITE)
        print_colored("  • Teste de confiabilidade com múltiplas execuções", Fore.WHITE)
        print_colored("  • Métricas de performance e recomendações", Fore.WHITE)
        print()
        
        print_colored("ARQUIVOS E PASTAS:", Fore.YELLOW)
        print_colored("  • Elementos salvos em: captured_elements/", Fore.WHITE)
        print_colored("  • Cada elemento em pasta própria com timestamp", Fore.WHITE)
        print_colored("  • Dados salvos em JSON com estrutura preservada", Fore.WHITE)
        print_colored("  • Use opção 5 para abrir a pasta no explorador", Fore.WHITE)
        print()
        
        print_colored("DICAS AVANÇADAS:", Fore.YELLOW)
        print_colored("  • O inspector faz até 3 tentativas de captura", Fore.WHITE)
        print_colored("  • Detecta automaticamente o framework usado", Fore.WHITE)
        print_colored("  • Gera múltiplos seletores por ordem de robustez", Fore.WHITE)
        print_colored("  • Seletores são validados automaticamente durante captura", Fore.WHITE)
        print_colored("  • Clique relativo funciona mesmo com janelas redimensionadas", Fore.WHITE)
        print_colored("  • Preserva estrutura complexa de dados no JSON", Fore.WHITE)
        print_colored("  • Use a opção 4 para testar seletores personalizados", Fore.WHITE)
        print()
        
        wait_for_keypress()
    
    def run(self):
        """
        Loop principal da aplicação
        
        Gerencia o ciclo de vida da aplicação e trata exceções
        """
        try:
            self.show_banner()
            
            while self.running:
                self.show_main_menu()
                choice = self.get_user_choice()
                
                if choice == "1":
                    self.capture_element_workflow()
                elif choice == "2":
                    self.capture_anchor_relative_workflow()
                elif choice == "3":
                    self.list_captured_elements()
                elif choice == "4":
                    self.test_xml_selector_workflow()
                elif choice == "5":
                    self.open_elements_folder()
                elif choice == "6":
                    self.show_help()
                elif choice == "7":
                    print_info("Encerrando UI Inspector...")
                    self.running = False
                else:
                    print_error("Opção inválida. Tente novamente.")
                    time.sleep(1)
        
        except KeyboardInterrupt:
            print()
            print_info("Encerrando UI Inspector...")
        except Exception as e:
            print_error(f"Erro inesperado: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            print_colored("Obrigado por usar o UI Inspector!", Fore.GREEN)

def main():
    """
    Função principal - ponto de entrada da aplicação
    
    Verifica dependências e sistema operacional antes de iniciar
    """
    # Verifica dependências
    try:
        import uiautomation
        import win32gui
        import win32api
        import win32con
        import psutil
        import colorama
    except ImportError as e:
        print(f"Erro: Dependência não encontrada - {e}")
        print("Execute: pip install -r requirements.txt")
        sys.exit(1)
    
    # Verifica se está rodando no Windows
    if os.name != 'nt':
        print("Erro: Este programa funciona apenas no Windows")
        print("Sistema detectado:", os.name)
        sys.exit(1)
    
    # Inicia aplicação
    app = UIInspectorApp()
    app.run()

if __name__ == "__main__":
    main()