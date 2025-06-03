"""
Inspector de Elementos UI para Windows Desktop
Versão 1 - Com detecção de janelas de destino e retry inteligente
"""
import time
import threading
import win32gui
import win32api
import win32con
import uiautomation as auto
from xml_selector_generator import XMLSelectorGenerator
from utils import *

# Importação opcional para debug avançado
try:
    import comtypes
    HAS_COMTYPES = True
except ImportError:
    HAS_COMTYPES = False

class ElementInspector:
    """
    Inspector principal para captura de elementos UI
    
    Implementa captura robusta com retry inteligente e detecção
    de elementos que podem abrir janelas.
    """
    
    def __init__(self):
        """Inicializa o inspector com gerador de XML"""
        self.xml_generator = XMLSelectorGenerator()
        self.is_capturing = False
        self.captured_element = None
        self.mouse_hook = None
        
    def start_capture_mode(self, element_name):
        """
        Inicia o modo de captura de elementos
        
        Args:
            element_name: Nome para identificar o elemento
            
        Returns:
            dict: Dados do elemento capturado ou None se cancelado
        """
        print_header("MODO DE CAPTURA ATIVADO")
        print_info("CTRL + Click no elemento para capturar | ESC para cancelar")
        
        self.is_capturing = True
        self.captured_element = None
        self.last_click_time = 0
        
        # Aguarda captura ou cancelamento
        while self.is_capturing:
            try:
                time.sleep(0.05)  # Resposta mais rápida (50ms)
                
                # Verifica se ESC foi pressionado
                if win32api.GetAsyncKeyState(win32con.VK_ESCAPE) & 0x8000:
                    print_warning("Captura cancelada pelo usuário")
                    self.is_capturing = False
                    return None
                
                # Verifica combinação CTRL + Click esquerdo
                ctrl_pressed = win32api.GetAsyncKeyState(win32con.VK_CONTROL) & 0x8000
                click_pressed = win32api.GetAsyncKeyState(win32con.VK_LBUTTON) & 0x8000
                
                if ctrl_pressed and click_pressed:
                    # Evita múltiplos triggers do mesmo click
                    current_time = time.time()
                    if current_time - self.last_click_time > 0.3:  # 300ms de debounce
                        self.last_click_time = current_time
                        return self._capture_element_at_cursor(element_name)
                    
            except KeyboardInterrupt:
                print_warning("Captura interrompida")
                self.is_capturing = False
                return None
        
        return None
    
    def _capture_element_at_cursor(self, element_name):
        """
        Captura elemento na posição atual do cursor com retry inteligente
        
        Implementa múltiplas tentativas para lidar com elementos instáveis
        ou que demoram para ficar disponíveis.
        
        Args:
            element_name: Nome para identificar o elemento
            
        Returns:
            dict: Dados do elemento capturado ou None se falhar
        """
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Obtém posição do cursor
                cursor_pos = win32gui.GetCursorPos()
                print_info(f"Capturando elemento na posição: {cursor_pos}")
                
                # Pequeno delay para garantir que o click foi processado
                time.sleep(0.1)
                
                # Busca elemento na posição do cursor
                element = auto.ControlFromPoint(cursor_pos[0], cursor_pos[1])
                
                if not element:
                    # Fallback: tenta obter elemento sob cursor diretamente
                    print_warning("Tentando método alternativo de captura...")
                    element = auto.GetCursorControl()
                
                if not element:
                    retry_count += 1
                    if retry_count < max_retries:
                        print_warning(f"Tentativa {retry_count}/{max_retries} falhou. Tentando novamente...")
                        time.sleep(0.2)
                        continue
                    else:
                        print_error("Nenhum elemento encontrado na posição do cursor")
                        print_warning("Tente clicar em uma área diferente do elemento")
                        self.is_capturing = False
                        return None
                
                # Verifica se é um elemento válido
                try:
                    # Força acesso a propriedades para validar elemento
                    _ = element.ControlTypeName
                    _ = element.BoundingRectangle
                    
                    # Verifica se não é o desktop
                    if element.ClassName == '#32769' or element.Name == 'Desktop':
                        print_warning("Capturou o desktop. Tente clicar em um elemento específico.")
                        retry_count += 1
                        if retry_count < max_retries:
                            time.sleep(0.2)
                            continue
                    
                except Exception:
                    retry_count += 1
                    if retry_count < max_retries:
                        print_warning(f"Elemento instável. Tentativa {retry_count}/{max_retries}...")
                        time.sleep(0.2)
                        continue
                    else:
                        print_error("Elemento não acessível via UIA")
                        print_warning("Este elemento pode não suportar automação")
                        self.is_capturing = False
                        return None
                
                # Elemento válido capturado
                element_display_name = element.Name or element.ClassName or element.ControlTypeName or 'Elemento válido'
                print_success(f"Elemento capturado: {element_display_name}")
                
                # Para o modo de captura
                self.is_capturing = False
                
                # Processa e salva o elemento
                return self._process_captured_element(element, element_name)
                
            except Exception as e:
                retry_count += 1
                if retry_count < max_retries:
                    print_warning(f"Erro na tentativa {retry_count}: {str(e)}")
                    time.sleep(0.2)
                else:
                    print_error(f"Erro ao capturar elemento após {max_retries} tentativas: {str(e)}")
                    self.is_capturing = False
                    return None
        
        return None
    
    def _process_captured_element(self, element, element_name):
        """
        Processa elemento capturado e extrai todas as informações
        
        Args:
            element: Elemento UI Automation capturado
            element_name: Nome para identificar o elemento
            
        Returns:
            dict: Dados processados do elemento ou None se falhar
        """
        try:
            print_info("Extraindo informações do elemento...")
            
            # Extrai informações básicas
            element_data = self._extract_element_properties(element)
            
            # Gera seletores XML
            print_info("Gerando seletores XML robustos...")
            xml_selectors = self.xml_generator.generate_robust_selector(element)
            element_data['xml_selectors'] = xml_selectors
            
            # Extrai informações da janela
            window_info = self._extract_window_info(element)
            element_data['window_info'] = window_info
            
            # Detecta possível janela de destino
            target_window_info = self._detect_target_window(element)
            element_data['target_window_detection'] = target_window_info
            
            # Extrai padrões suportados
            patterns = self._extract_supported_patterns(element)
            element_data['supported_patterns'] = patterns
            
            # Salva dados
            folder_path = create_element_folder(element_name)
            file_path = save_element_data(folder_path, element_data)
            
            print_success(f"Elemento salvo em: {folder_path}")
            self._display_capture_summary(element_data)
            
            return {
                'folder_path': folder_path,
                'file_path': file_path,
                'element_data': element_data
            }
            
        except Exception as e:
            print_error(f"Erro ao processar elemento: {str(e)}")
            return None
    
    def _extract_element_properties(self, element):
        """
        Extrai todas as propriedades do elemento
        
        Args:
            element: Elemento UI Automation
            
        Returns:
            dict: Propriedades extraídas do elemento
        """
        try:
            rect = element.BoundingRectangle
            
            return {
                # Propriedades principais
                'automation_id': getattr(element, 'AutomationId', '') or '',
                'name': getattr(element, 'Name', '') or '',
                'class_name': getattr(element, 'ClassName', '') or '',
                'control_type': getattr(element, 'ControlTypeName', '') or '',
                'localized_control_type': getattr(element, 'LocalizedControlType', '') or '',
                'framework_id': getattr(element, 'FrameworkId', '') or '',
                'framework_type': self._get_framework_type(element),
                'process_id': getattr(element, 'ProcessId', 0),
                'runtime_id': self._safe_get_runtime_id(element),
                
                # Estados
                'is_enabled': getattr(element, 'IsEnabled', True),
                'is_visible': not getattr(element, 'IsOffscreen', False),
                'is_keyboard_focusable': getattr(element, 'IsKeyboardFocusable', False),
                'has_keyboard_focus': getattr(element, 'HasKeyboardFocus', False),
                'is_content_element': getattr(element, 'IsContentElement', True),
                'is_control_element': getattr(element, 'IsControlElement', True),
                
                # Geometria
                'bounding_rectangle': {
                    'left': rect.left if rect else 0,
                    'top': rect.top if rect else 0,
                    'right': rect.right if rect else 0,
                    'bottom': rect.bottom if rect else 0,
                    'width': (rect.right - rect.left) if rect else 0,
                    'height': (rect.bottom - rect.top) if rect else 0
                },
                
                # Informações do processo
                'process_info': get_process_info(getattr(element, 'ProcessId', 0)),
                
                # Valor (se disponível)
                'value': self._get_element_value(element),
                
                # Hierarquia
                'parent_info': self._get_parent_info(element),
                'children_count': self._get_children_count(element)
            }
            
        except Exception as e:
            return {'error': f'Erro ao extrair propriedades: {str(e)}'}
    
    def _safe_get_runtime_id(self, element):
        """
        Obtém RuntimeId de forma segura
        
        Args:
            element: Elemento UI Automation
            
        Returns:
            list: RuntimeId ou lista vazia
        """
        try:
            runtime_id = getattr(element, 'RuntimeId', None)
            if runtime_id:
                return list(runtime_id)
            return []
        except Exception:
            return []
    
    def _get_framework_type(self, element):
        """
        Determina o tipo de framework da aplicação
        
        Analisa FrameworkId e ClassName para identificar a tecnologia
        
        Args:
            element: Elemento UI Automation
            
        Returns:
            str: Tipo de framework detectado
        """
        try:
            framework_id = getattr(element, 'FrameworkId', '')
            class_name = getattr(element, 'ClassName', '')
            
            if framework_id:
                return framework_id
            
            # Detecta framework baseado na classe
            if class_name:
                if 'WPF' in class_name or class_name.startswith('Wpf'):
                    return 'WPF'
                elif class_name.startswith('WindowsForms') or 'WinForms' in class_name:
                    return 'WinForms'
                elif 'TForm' in class_name or class_name.startswith('T'):
                    return 'Delphi/VCL'
                elif 'SunAwtFrame' in class_name or 'Swing' in class_name:
                    return 'Java Swing'
                elif class_name.startswith('Chrome') or class_name.startswith('Mozilla'):
                    return 'Web Browser'
            
            return 'Unknown'
        except Exception:
            return 'Unknown'
    
    def _get_element_value(self, element):
        """
        Extrai valor do elemento se disponível
        
        Tenta múltiplas estratégias para obter o valor
        
        Args:
            element: Elemento UI Automation
            
        Returns:
            str: Valor do elemento ou None
        """
        try:
            # Tenta propriedade Value direta primeiro
            if hasattr(element, 'GetValuePattern'):
                try:
                    value_pattern = element.GetValuePattern()
                    if value_pattern:
                        return value_pattern.Value
                except:
                    pass
            
            # Tenta propriedade Value simples
            value = getattr(element, 'Value', None)
            if value:
                return value
            
            # Para elementos de texto, tenta TextPattern
            try:
                if hasattr(element, 'GetTextPattern'):
                    text_pattern = element.GetTextPattern()
                    if text_pattern:
                        return text_pattern.DocumentRange.GetText()
            except:
                pass
            
            # Último recurso: tenta Name se não tem valor específico
            name = getattr(element, 'Name', '')
            if name and len(name) < 100:  # Evita textos muito longos
                return name
            
            return None
            
        except Exception:
            return None
    
    def _detect_target_window(self, element):
        """
        Detecta possível janela de destino para elementos que abrem janelas
        
        Analisa o tipo de controle e nome para identificar elementos
        que provavelmente abrem janelas quando acionados.
        
        Args:
            element: Elemento UI Automation
            
        Returns:
            dict: Informações sobre possível janela de destino
        """
        try:
            # Verifica se é um elemento que pode abrir janelas
            control_type = getattr(element, 'ControlTypeName', '')
            name = getattr(element, 'Name', '')
            
            # Tipos de controle que geralmente abrem janelas
            window_opener_types = ['ButtonControl', 'MenuItemControl', 'HyperlinkControl']
            
            # Palavras-chave que indicam abertura de janela
            window_keywords = [
                'abrir', 'open', 'novo', 'new', 'browse', 'procurar', 
                'selecionar', 'select', '...', 'configurar', 'settings',
                'opções', 'options', 'propriedades', 'properties', 'editar',
                'edit', 'adicionar', 'add', 'criar', 'create', 'detalhes',
                'details', 'mais', 'more', 'avançado', 'advanced'
            ]
            
            # Verifica se é um elemento que pode abrir janela
            is_window_opener = (
                control_type in window_opener_types or
                any(keyword in name.lower() for keyword in window_keywords)
            )
            
            if is_window_opener:
                # Tenta detectar padrão de invocação
                try:
                    invoke_pattern = element.GetInvokePattern()
                    if invoke_pattern:
                        return {
                            'likely_opens_window': True,
                            'control_type': control_type,
                            'button_text': name,
                            'detection_hints': [
                                'Este elemento provavelmente abre uma janela quando clicado',
                                'Considere capturar a janela de destino separadamente',
                                'Use o nome da janela de destino no seletor quando automatizar',
                                'Para automação robusta, implemente espera pela janela aparecer'
                            ]
                        }
                except:
                    pass
            
            return {'likely_opens_window': False}
            
        except Exception as e:
            return {'error': f'Erro ao detectar janela de destino: {str(e)}'}
    
    def _extract_window_info(self, element):
        """
        Extrai informações da janela pai
        
        Navega pela hierarquia até encontrar a janela principal
        
        Args:
            element: Elemento UI Automation
            
        Returns:
            dict: Informações da janela ou erro
        """
        try:
            # Navega até encontrar a janela principal
            current = element
            max_depth = 10  # Evita loops infinitos
            depth = 0
            
            while current and depth < max_depth:
                if current.ControlTypeName == 'WindowControl':
                    rect = current.BoundingRectangle
                    return {
                        'title': current.Name or '',
                        'class_name': current.ClassName or '',
                        'automation_id': current.AutomationId or '',
                        'process_id': current.ProcessId,
                        'is_modal': getattr(current, 'IsModal', False),
                        'is_topmost': getattr(current, 'IsTopmost', False),
                        'window_rectangle': {
                            'left': rect.left,
                            'top': rect.top,
                            'right': rect.right,
                            'bottom': rect.bottom,
                            'width': rect.right - rect.left,
                            'height': rect.bottom - rect.top
                        }
                    }
                
                parent = current.GetParentControl()
                if parent == current or not parent:
                    break
                current = parent
                depth += 1
                
            return {'error': 'Janela pai não encontrada'}
            
        except Exception as e:
            return {'error': f'Erro ao extrair informações da janela: {str(e)}'}
    
    def _extract_supported_patterns(self, element):
        """
        Extrai padrões de automação suportados
        
        Verifica todos os padrões e extrai informações específicas de cada um
        
        Args:
            element: Elemento UI Automation
            
        Returns:
            dict: Padrões suportados com informações detalhadas
        """
        patterns = {}
        
        # Lista de padrões para verificar (nome_método, nome_padrão)
        pattern_checks = [
            ('GetInvokePattern', 'InvokePattern'),
            ('GetValuePattern', 'ValuePattern'),
            ('GetTextPattern', 'TextPattern'),
            ('GetTogglePattern', 'TogglePattern'),
            ('GetSelectionPattern', 'SelectionPattern'),
            ('GetSelectionItemPattern', 'SelectionItemPattern'),
            ('GetExpandCollapsePattern', 'ExpandCollapsePattern'),
            ('GetScrollPattern', 'ScrollPattern'),
            ('GetGridPattern', 'GridPattern'),
            ('GetTablePattern', 'TablePattern'),
            ('GetWindowPattern', 'WindowPattern'),
            ('GetTransformPattern', 'TransformPattern'),
            ('GetRangeValuePattern', 'RangeValuePattern')
        ]
        
        for method_name, pattern_name in pattern_checks:
            try:
                if hasattr(element, method_name):
                    pattern = getattr(element, method_name)()
                    if pattern:
                        patterns[pattern_name] = self._extract_pattern_info(pattern, pattern_name)
                    else:
                        patterns[pattern_name] = False
                else:
                    patterns[pattern_name] = False
            except Exception:
                patterns[pattern_name] = False
        
        return patterns
    
    def _extract_pattern_info(self, pattern, pattern_name):
        """
        Extrai informações específicas de cada padrão
        
        Args:
            pattern: Objeto do padrão
            pattern_name: Nome do padrão
            
        Returns:
            dict: Informações extraídas do padrão
        """
        try:
            info = {'supported': True}
            
            if pattern_name == 'ValuePattern':
                info['value'] = getattr(pattern, 'Value', None)
                info['is_read_only'] = getattr(pattern, 'IsReadOnly', None)
            
            elif pattern_name == 'TogglePattern':
                toggle_state = getattr(pattern, 'ToggleState', None)
                info['toggle_state'] = str(toggle_state) if toggle_state is not None else None
            
            elif pattern_name == 'RangeValuePattern':
                info['value'] = getattr(pattern, 'Value', None)
                info['minimum'] = getattr(pattern, 'Minimum', None)
                info['maximum'] = getattr(pattern, 'Maximum', None)
                info['is_read_only'] = getattr(pattern, 'IsReadOnly', None)
            
            elif pattern_name == 'ExpandCollapsePattern':
                expand_state = getattr(pattern, 'ExpandCollapseState', None)
                info['expand_collapse_state'] = str(expand_state) if expand_state is not None else None
            
            elif pattern_name == 'ScrollPattern':
                info['horizontal_scroll_percent'] = getattr(pattern, 'HorizontalScrollPercent', None)
                info['vertical_scroll_percent'] = getattr(pattern, 'VerticalScrollPercent', None)
                info['horizontal_view_size'] = getattr(pattern, 'HorizontalViewSize', None)
                info['vertical_view_size'] = getattr(pattern, 'VerticalViewSize', None)
            
            elif pattern_name == 'SelectionPattern':
                info['can_select_multiple'] = getattr(pattern, 'CanSelectMultiple', None)
                info['is_selection_required'] = getattr(pattern, 'IsSelectionRequired', None)
            
            elif pattern_name == 'WindowPattern':
                info['can_maximize'] = getattr(pattern, 'CanMaximize', None)
                info['can_minimize'] = getattr(pattern, 'CanMinimize', None)
                info['is_modal'] = getattr(pattern, 'IsModal', None)
                info['is_topmost'] = getattr(pattern, 'IsTopmost', None)
            
            return info
            
        except Exception as e:
            return {'supported': True, 'error': str(e)}
    
    def _get_parent_info(self, element):
        """
        Obtém informações básicas do elemento pai
        
        Args:
            element: Elemento UI Automation
            
        Returns:
            dict: Informações do pai ou None
        """
        try:
            parent = element.GetParentControl()
            if parent and parent != element:
                return {
                    'automation_id': parent.AutomationId or '',
                    'name': parent.Name or '',
                    'class_name': parent.ClassName or '',
                    'control_type': parent.ControlTypeName or ''
                }
            return None
        except Exception:
            return None
    
    def _get_children_count(self, element):
        """
        Conta elementos filhos
        
        Args:
            element: Elemento UI Automation
            
        Returns:
            int: Número de elementos filhos
        """
        try:
            children = element.GetChildren()
            return len(children) if children else 0
        except Exception:
            return 0
    
    def _display_capture_summary(self, element_data):
        """
        Exibe resumo do elemento capturado
        
        Mostra informações principais de forma concisa
        
        Args:
            element_data: Dados do elemento capturado
        """
        print_header("RESUMO DO ELEMENTO CAPTURADO")
        
        # Propriedades principais
        print_colored(f"AutomationId: {element_data.get('automation_id', 'N/A')}", Fore.CYAN)
        print_colored(f"Name: {element_data.get('name', 'N/A')}", Fore.CYAN)
        print_colored(f"ClassName: {element_data.get('class_name', 'N/A')}", Fore.CYAN)
        print_colored(f"ControlType: {element_data.get('control_type', 'N/A')}", Fore.CYAN)
        print_colored(f"FrameworkType: {element_data.get('framework_type', 'N/A')}", Fore.CYAN)
        print_colored(f"ProcessId: {element_data.get('process_id', 'N/A')}", Fore.CYAN)
        
        # Exibe informações da janela
        window_info = element_data.get('window_info', {})
        if window_info and not window_info.get('error'):
            print_colored(f"Janela: {window_info.get('title', 'N/A')}", Fore.YELLOW)
            print_colored(f"Classe da Janela: {window_info.get('class_name', 'N/A')}", Fore.YELLOW)
        
        # Exibe detecção de janela de destino se relevante
        target_window = element_data.get('target_window_detection', {})
        if target_window.get('likely_opens_window'):
            print_colored("Detecção: Este elemento pode abrir uma janela", Fore.MAGENTA)
        
        # Exibe padrões suportados
        patterns = element_data.get('supported_patterns', {})
        supported = [name for name, info in patterns.items() if info and info != False]
        if supported:
            print_colored(f"Padrões suportados: {', '.join(supported)}", Fore.GREEN)
        
        # Exibe primeiro seletor XML
        selectors = element_data.get('xml_selectors', [])
        if selectors:
            print_colored("Seletor XML principal:", Fore.MAGENTA)
            print_colored(selectors[0], Fore.WHITE)