"""
Inspector de Elementos UI para Windows Desktop
Versão 2 - Com suporte para elemento âncora e clique relativo
"""
import time
import threading
import win32gui
import win32api
import win32con
import uiautomation as auto
from xml_selector_generator import XMLSelectorGenerator
from xml_selector_validator import XMLSelectorValidator
from xml_selector_ultra_robust import UltraRobustSelectorGenerator
from xml_selector_optimized import OptimizedSelectorGenerator
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
    
    Implementa captura robusta com retry inteligente, detecção
    de elementos que podem abrir janelas e clique relativo com âncora.
    """
    
    def __init__(self):
        """Inicializa o inspector com gerador de XML e validador"""
        self.xml_generator = XMLSelectorGenerator()
        self.xml_validator = XMLSelectorValidator()
        self.ultra_robust_generator = UltraRobustSelectorGenerator()
        self.optimized_generator = OptimizedSelectorGenerator()  # Novo gerador otimizado
        self.is_capturing = False
        self.captured_element = None
        self.mouse_hook = None
        self.anchor_element = None  # Elemento âncora para clique relativo
        self.enable_validation = True  # Controla se validação automática está ativa
        self.enable_ultra_robust = True  # Controla se geração ultra-robusta está ativa
        
    def start_capture_mode(self, element_name, capture_type="element"):
        """
        Inicia o modo de captura de elementos
        
        Args:
            element_name: Nome para identificar o elemento
            capture_type: Tipo de captura ("element" ou "anchor_relative")
            
        Returns:
            dict: Dados do elemento capturado ou None se cancelado
        """
        if capture_type == "anchor_relative":
            return self._capture_anchor_and_relative_click(element_name)
        else:
            return self._capture_single_element(element_name)
    
    def _capture_single_element(self, element_name):
        """
        Captura um único elemento (modo tradicional)
        
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
    
    def _capture_anchor_and_relative_click(self, element_name):
        """
        Captura elemento âncora e ponto de clique relativo
        
        Args:
            element_name: Nome para identificar o conjunto âncora+clique
            
        Returns:
            dict: Dados do elemento âncora e clique relativo
        """
        print_header("MODO DE CAPTURA COM ÂNCORA")
        
        # Passo 1: Capturar elemento âncora
        print_info("PASSO 1: Capturar Elemento Âncora")
        print_warning("CTRL + SHIFT + Click no elemento âncora | ESC para cancelar")
        
        self.is_capturing = True
        self.anchor_element = None
        self.last_click_time = 0
        
        while self.is_capturing:
            try:
                time.sleep(0.05)
                
                # Verifica ESC
                if win32api.GetAsyncKeyState(win32con.VK_ESCAPE) & 0x8000:
                    print_warning("Captura cancelada pelo usuário")
                    self.is_capturing = False
                    return None
                
                # Verifica CTRL + SHIFT + Click
                ctrl_pressed = win32api.GetAsyncKeyState(win32con.VK_CONTROL) & 0x8000
                shift_pressed = win32api.GetAsyncKeyState(win32con.VK_SHIFT) & 0x8000
                click_pressed = win32api.GetAsyncKeyState(win32con.VK_LBUTTON) & 0x8000
                
                if ctrl_pressed and shift_pressed and click_pressed:
                    current_time = time.time()
                    if current_time - self.last_click_time > 0.3:
                        self.last_click_time = current_time
                        
                        # Captura elemento âncora
                        cursor_pos = win32gui.GetCursorPos()
                        anchor_element = self._capture_element_at_position(cursor_pos)
                        
                        if anchor_element:
                            self.anchor_element = anchor_element
                            anchor_name = anchor_element.get('name') or anchor_element.get('class_name') or 'Elemento'
                            print_success(f"Elemento âncora capturado: {anchor_name}")
                            self.is_capturing = False
                        else:
                            print_error("Falha ao capturar elemento âncora")
                
            except KeyboardInterrupt:
                print_warning("Captura interrompida")
                return None
        
        if not self.anchor_element:
            return None
        
        # Passo 2: Capturar ponto de clique relativo
        print()
        print_info("PASSO 2: Marcar Ponto de Clique Relativo")
        print_warning("CTRL + Click onde deseja clicar (relativo ao âncora) | ESC para cancelar")
        
        self.is_capturing = True
        relative_click_pos = None
        
        while self.is_capturing:
            try:
                time.sleep(0.05)
                
                # Verifica ESC
                if win32api.GetAsyncKeyState(win32con.VK_ESCAPE) & 0x8000:
                    print_warning("Captura de clique relativo cancelada")
                    self.is_capturing = False
                    return None
                
                # Verifica CTRL + Click (sem SHIFT desta vez)
                ctrl_pressed = win32api.GetAsyncKeyState(win32con.VK_CONTROL) & 0x8000
                shift_pressed = win32api.GetAsyncKeyState(win32con.VK_SHIFT) & 0x8000
                click_pressed = win32api.GetAsyncKeyState(win32con.VK_LBUTTON) & 0x8000
                
                if ctrl_pressed and not shift_pressed and click_pressed:
                    current_time = time.time()
                    if current_time - self.last_click_time > 0.3:
                        self.last_click_time = current_time
                        
                        # Captura posição do clique
                        relative_click_pos = win32gui.GetCursorPos()
                        print_success(f"Ponto de clique capturado: {relative_click_pos}")
                        self.is_capturing = False
                
            except KeyboardInterrupt:
                print_warning("Captura interrompida")
                return None
        
        if not relative_click_pos:
            return None
        
        # Processa e salva dados do conjunto âncora + clique relativo
        return self._process_anchor_relative_capture(
            self.anchor_element, 
            relative_click_pos, 
            element_name
        )
    
    def _capture_element_at_position(self, position):
        """
        Captura elemento em uma posição específica
        
        Args:
            position: Tupla (x, y) com a posição
            
        Returns:
            dict: Dados do elemento ou None
        """
        try:
            element = auto.ControlFromPoint(position[0], position[1])
            
            if not element:
                element = auto.GetCursorControl()
            
            if not element:
                return None
            
            # Valida elemento
            try:
                _ = element.ControlTypeName
                _ = element.BoundingRectangle
                
                if element.ClassName == '#32769' or element.Name == 'Desktop':
                    return None
            except:
                return None
            
            # Extrai dados do elemento
            return self._extract_element_properties(element)
            
        except Exception as e:
            print_error(f"Erro ao capturar elemento: {str(e)}")
            return None
    
    def _process_anchor_relative_capture(self, anchor_data, click_position, element_name):
        """
        Processa dados de captura âncora + clique relativo
        
        Args:
            anchor_data: Dados do elemento âncora
            click_position: Posição (x, y) do clique
            element_name: Nome para identificar o conjunto
            
        Returns:
            dict: Dados processados
        """
        try:
            print_info("Processando captura com âncora e clique relativo...")
            
            # Obtém informações da janela do âncora
            window_info = anchor_data.get('window_info', {})
            if not window_info or window_info.get('error'):
                print_error("Não foi possível obter informações da janela do âncora")
                return None
            
            # Calcula posições relativas
            anchor_rect = anchor_data.get('bounding_rectangle', {})
            window_rect = window_info.get('window_rectangle', {})
            
            if not anchor_rect or not window_rect:
                print_error("Não foi possível obter geometria do âncora ou janela")
                return None
            
            # Calcula offset relativo ao âncora
            anchor_relative_x = click_position[0] - anchor_rect['left']
            anchor_relative_y = click_position[1] - anchor_rect['top']
            
            # Calcula offset relativo à janela
            window_relative_x = click_position[0] - window_rect['left']
            window_relative_y = click_position[1] - window_rect['top']
            
            # Calcula percentuais relativos ao tamanho da janela
            window_width = window_rect['width']
            window_height = window_rect['height']
            
            window_percent_x = (window_relative_x / window_width) * 100 if window_width > 0 else 0
            window_percent_y = (window_relative_y / window_height) * 100 if window_height > 0 else 0
            
            # Monta estrutura de dados
            capture_data = {
                'capture_type': 'anchor_relative',
                'anchor_element': anchor_data,
                'relative_click': {
                    'absolute_position': {
                        'x': click_position[0],
                        'y': click_position[1]
                    },
                    'anchor_relative': {
                        'offset_x': anchor_relative_x,
                        'offset_y': anchor_relative_y,
                        'description': f"Clique a {anchor_relative_x}px à direita e {anchor_relative_y}px abaixo do âncora"
                    },
                    'window_relative': {
                        'offset_x': window_relative_x,
                        'offset_y': window_relative_y,
                        'percent_x': round(window_percent_x, 2),
                        'percent_y': round(window_percent_y, 2),
                        'description': f"Clique a {window_percent_x:.1f}% da largura e {window_percent_y:.1f}% da altura da janela"
                    }
                },
                'window_context': {
                    'width': window_width,
                    'height': window_height,
                    'title': window_info.get('title', ''),
                    'class_name': window_info.get('class_name', '')
                }
            }
            
            # Gera seletores XML especiais para clique relativo
            print_info("Gerando seletores XML para clique relativo...")
            xml_selectors = self.xml_generator.generate_relative_click_selectors(
                anchor_data, 
                capture_data['relative_click']
            )
            capture_data['xml_selectors'] = xml_selectors
            
            # Salva dados
            folder_path = create_element_folder(element_name)
            file_path = save_element_data(folder_path, capture_data)
            
            print_success(f"Captura âncora+clique salva em: {folder_path}")
            self._display_anchor_relative_summary(capture_data)
            
            return {
                'folder_path': folder_path,
                'file_path': file_path,
                'element_data': capture_data
            }
            
        except Exception as e:
            print_error(f"Erro ao processar captura âncora+clique: {str(e)}")
            return None
    
    def _display_anchor_relative_summary(self, capture_data):
        """
        Exibe resumo da captura âncora + clique relativo
        
        Args:
            capture_data: Dados da captura
        """
        print_header("RESUMO DA CAPTURA ÂNCORA + CLIQUE RELATIVO")
        
        # Informações do âncora
        anchor = capture_data.get('anchor_element', {})
        print_colored("ELEMENTO ÂNCORA:", Fore.YELLOW)
        print_colored(f"  AutomationId: {anchor.get('automation_id', 'N/A')}", Fore.CYAN)
        print_colored(f"  Name: {anchor.get('name', 'N/A')}", Fore.CYAN)
        print_colored(f"  ControlType: {anchor.get('control_type', 'N/A')}", Fore.CYAN)
        print()
        
        # Informações do clique relativo
        relative = capture_data.get('relative_click', {})
        print_colored("CLIQUE RELATIVO:", Fore.YELLOW)
        
        anchor_rel = relative.get('anchor_relative', {})
        print_colored(f"  Offset do âncora: ({anchor_rel.get('offset_x')}px, {anchor_rel.get('offset_y')}px)", Fore.GREEN)
        
        window_rel = relative.get('window_relative', {})
        print_colored(f"  Posição na janela: {window_rel.get('percent_x')}% x {window_rel.get('percent_y')}%", Fore.GREEN)
        print()
        
        # Contexto da janela
        window_ctx = capture_data.get('window_context', {})
        print_colored("CONTEXTO DA JANELA:", Fore.YELLOW)
        print_colored(f"  Título: {window_ctx.get('title', 'N/A')}", Fore.WHITE)
        print_colored(f"  Tamanho: {window_ctx.get('width')} x {window_ctx.get('height')} pixels", Fore.WHITE)
        
        # Primeiro seletor
        selectors = capture_data.get('xml_selectors', [])
        if selectors:
            print()
            print_colored("SELETOR PRINCIPAL:", Fore.MAGENTA)
            print_colored(selectors[0], Fore.WHITE)
    
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
            element_data['capture_type'] = 'single_element'  # Marca tipo de captura
            
            # Tenta primeiro o gerador otimizado (mais efetivo)
            print_info("🎯 Tentando gerador OTIMIZADO primeiro...")
            optimized_result = self.optimized_generator.generate_optimized_selector(element)
            
            if optimized_result and optimized_result['generation_metadata']['strategies_working'] > 0:
                # Sucesso com gerador otimizado
                element_data['xml_selector_optimized'] = optimized_result['optimized_selector']
                element_data['optimized_metadata'] = optimized_result['generation_metadata']
                element_data['working_selectors'] = optimized_result['working_selectors']
                element_data['element_analysis'] = optimized_result['element_analysis']
                
                reliability_score = optimized_result['generation_metadata']['reliability_score']
                working_count = optimized_result['generation_metadata']['strategies_working']
                print_success(f"✅ Gerador otimizado funcionou: {working_count} estratégias, {reliability_score:.1f}% confiabilidade!")
            elif self.enable_ultra_robust:
                print_warning("⚠️ Gerador otimizado falhou - tentando ultra-robusto...")
                
                ultra_robust_result = self.ultra_robust_generator.generate_ultra_robust_selector(element)
                
                if ultra_robust_result:
                    # Seletor ultra-robusto principal
                    element_data['xml_selector_ultra_robust'] = ultra_robust_result['ultra_robust_selector']
                    element_data['ultra_robust_metadata'] = ultra_robust_result['generation_metadata']
                    element_data['stability_analysis'] = ultra_robust_result['stability_analysis']
                    element_data['available_strategies'] = ultra_robust_result['strategies']
                    
                    # Gera relatório de estabilidade
                    stability_report = self.ultra_robust_generator.get_stability_report(
                        ultra_robust_result['stability_analysis'], 
                        ultra_robust_result['stability_analysis']
                    )
                    element_data['stability_report'] = stability_report
                    
                    reliability_score = ultra_robust_result['generation_metadata']['reliability_score']
                    print_success(f"🏆 Seletor ultra-robusto gerado com {reliability_score:.1f}% de confiabilidade!")
                    print_info(f"📊 {len(ultra_robust_result['strategies'])} estratégias validadas automaticamente")
                    
                    # Mantém seletores tradicionais como backup
                    if self.enable_validation:
                        validation_result = self.xml_validator.generate_and_validate_selectors(element, validate_immediately=True)
                        element_data['xml_selectors_backup'] = validation_result.get('valid_selectors', [])
                    else:
                        element_data['xml_selectors_backup'] = self.xml_generator.generate_robust_selector(element)
                        
                else:
                    print_warning("⚠️ Ultra-robusto também falhou - usando método tradicional")
                    # Fallback final para método tradicional
                    if self.enable_validation:
                        validation_result = self.xml_validator.generate_and_validate_selectors(element, validate_immediately=True)
                        element_data['xml_selectors'] = validation_result.get('valid_selectors', [])
                    else:
                        element_data['xml_selectors'] = self.xml_generator.generate_robust_selector(element)
            else:
                # Método tradicional (modo de compatibilidade)
                if self.enable_validation:
                    print_info("Gerando e validando seletores XML executáveis...")
                    validation_result = self.xml_validator.generate_and_validate_selectors(element, validate_immediately=True)
                    
                    if validation_result['valid_selectors']:
                        element_data['xml_selectors'] = validation_result['valid_selectors']
                        element_data['xml_selectors_legacy'] = self.xml_generator.generate_robust_selector(element)
                        element_data['validation_report'] = {
                            'total_generated': len(validation_result['valid_selectors']) + len(validation_result['invalid_selectors']),
                            'total_valid': len(validation_result['valid_selectors']),
                            'validation_time': validation_result['validation_time'],
                            'generation_time': validation_result['generation_time']
                        }
                        print_success(f"✓ {len(validation_result['valid_selectors'])} seletores validados automaticamente")
                    else:
                        print_warning("Nenhum seletor validado - usando seletores tradicionais")
                        element_data['xml_selectors'] = self.xml_generator.generate_robust_selector(element)
                        element_data['validation_report'] = {'error': 'Falha na validação automática'}
                else:
                    print_info("Gerando seletores XML tradicionais...")
                    element_data['xml_selectors'] = self.xml_generator.generate_robust_selector(element)
            
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
                'children_count': self._get_children_count(element),
                
                # Informações da janela já extraídas aqui
                'window_info': self._extract_window_info(element)
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
        
        # Exibe seletor otimizado se disponível (prioridade sobre ultra-robusto)
        optimized_selector = element_data.get('xml_selector_optimized')
        if optimized_selector:
            print()
            print_colored("🎯 SELETOR XML OTIMIZADO:", Fore.GREEN)
            print_colored(optimized_selector, Fore.WHITE)
            
            # Exibe metadata do seletor otimizado
            optimized_metadata = element_data.get('optimized_metadata', {})
            if optimized_metadata:
                reliability = optimized_metadata.get('reliability_score', 0)
                working_strategies = optimized_metadata.get('strategies_working', 0)
                tested_strategies = optimized_metadata.get('strategies_tested', 0)
                print_colored(f"🏆 Confiabilidade: {reliability:.1f}% | Estratégias funcionando: {working_strategies}/{tested_strategies}", Fore.GREEN)
            
            # Exibe estratégias funcionando
            working_selectors = element_data.get('working_selectors', [])
            if working_selectors:
                print_colored("✅ Estratégias funcionando:", Fore.CYAN)
                for i, selector in enumerate(working_selectors[:3], 1):  # Mostra as 3 melhores
                    exec_time = selector.get('execution_time', 0)
                    print_colored(f"  {i}. {selector['description']} ({exec_time:.2f}s)", Fore.WHITE)
                    
        # Exibe seletor ultra-robusto se disponível e não houver otimizado
        elif element_data.get('xml_selector_ultra_robust'):
            ultra_robust_selector = element_data.get('xml_selector_ultra_robust')
            print()
            print_colored("🎯 SELETOR XML ULTRA-ROBUSTO:", Fore.MAGENTA)
            print_colored(ultra_robust_selector, Fore.WHITE)
            
            # Exibe metadata do seletor ultra-robusto
            metadata = element_data.get('ultra_robust_metadata', {})
            if metadata:
                reliability = metadata.get('reliability_score', 0)
                strategy = metadata.get('recommended_strategy', 'N/A')
                print_colored(f"🏆 Confiabilidade: {reliability:.1f}% | Estratégia: {strategy}", Fore.GREEN)
            
            # Exibe análise de estabilidade
            stability_report = element_data.get('stability_report', {})
            if stability_report.get('recommendations'):
                print_colored("💡 Recomendações:", Fore.CYAN)
                for rec in stability_report['recommendations'][:2]:  # Mostra apenas as 2 primeiras
                    print_colored(f"  • {rec}", Fore.WHITE)
                    
            if stability_report.get('warnings'):
                print_colored("⚠️ Avisos:", Fore.YELLOW)
                for warning in stability_report['warnings'][:1]:  # Mostra apenas o primeiro
                    print_colored(f"  • {warning}", Fore.YELLOW)
        else:
            # Fallback para seletores tradicionais
            selectors = element_data.get('xml_selectors', [])
            if selectors:
                print_colored("Seletor XML principal:", Fore.MAGENTA)
                print_colored(selectors[0], Fore.WHITE)
                
            # Exibe informações de validação se disponíveis
            validation_report = element_data.get('validation_report', {})
            if validation_report and 'total_valid' in validation_report:
                print_colored(f"Validação: {validation_report['total_valid']}/{validation_report['total_generated']} seletores válidos", Fore.GREEN)
    
    def test_xml_selector(self, xml_selector):
        """
        Testa um seletor XML fornecido pelo usuário
        
        Args:
            xml_selector: String XML do seletor para testar
            
        Returns:
            dict: Resultado do teste
        """
        print_info("Testando seletor XML...")
        
        try:
            # Valida o seletor
            validation_result = self.xml_validator.validate_single_selector(xml_selector)
            
            if validation_result['valid']:
                print_success("✓ Seletor XML válido!")
                
                # Testa confiabilidade
                reliability_result = self.xml_validator.test_selector_reliability(xml_selector, test_count=3)
                
                return {
                    'success': True,
                    'validation': validation_result,
                    'reliability': reliability_result,
                    'message': f"Seletor válido com {reliability_result['reliability_percentage']:.1f}% de confiabilidade"
                }
            else:
                print_error("✗ Seletor XML inválido")
                return {
                    'success': False,
                    'validation': validation_result,
                    'message': f"Seletor inválido: {validation_result.get('errors', ['Erro desconhecido'])[0]}"
                }
                
        except Exception as e:
            print_error(f"Erro ao testar seletor: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': f"Erro durante teste: {str(e)}"
            }
    
    def execute_xml_selector_action(self, xml_selector, action_type="click"):
        """
        Executa ação em elemento encontrado por seletor XML
        
        Args:
            xml_selector (str): Seletor XML
            action_type (str): Tipo de ação a executar ("click", "double_click", "right_click")
            
        Returns:
            dict: Resultado da execução
        """
        print_info(f"🎯 Executando ação '{action_type}' via seletor XML ultra-robusto...")
        
        try:
            # Usa o executor do ultra-robusto que tem melhor compatibilidade
            result = self.ultra_robust_generator.executor.execute_click_action(
                xml_selector, 
                action_type=action_type,
                timeout=5
            )
            
            if result['success']:
                print_success(f"✓ Ação '{action_type}' executada com sucesso!")
                print_colored(f"Método usado: {result.get('method', 'N/A')}", Fore.GREEN)
                if 'position' in result:
                    print_colored(f"Posição: {result['position']}", Fore.CYAN)
                if 'element_info' in result:
                    element_info = result['element_info']
                    print_colored(f"Elemento: {element_info.get('name', 'N/A')} ({element_info.get('control_type', 'N/A')})", Fore.CYAN)
            else:
                print_error(f"✗ Falha ao executar ação: {result.get('error', 'Erro desconhecido')}")
            
            return result
            
        except Exception as e:
            error_msg = f"Erro ao executar ação: {str(e)}"
            print_error(error_msg)
            return {
                'success': False,
                'error': str(e),
                'message': error_msg
            }
    
    def optimize_element_selectors(self, element, element_name):
        """
        Otimiza seletores para um elemento já capturado
        
        Args:
            element: Elemento UI Automation
            element_name: Nome do elemento
            
        Returns:
            dict: Resultado da otimização
        """
        print_info("Otimizando seletores para máxima confiabilidade...")
        
        try:
            optimization_result = self.xml_validator.optimize_selectors(element, max_selectors=3)
            
            if optimization_result['optimized_selectors']:
                print_success(f"✓ {len(optimization_result['optimized_selectors'])} seletores otimizados")
                
                # Salva resultado da otimização
                folder_path = create_element_folder(f"{element_name}_optimized")
                
                optimized_data = {
                    'element_name': element_name,
                    'capture_type': 'optimized_selectors',
                    'optimized_selectors': optimization_result['optimized_selectors'],
                    'optimization_report': optimization_result['optimization_report'],
                    'generated_at': time.time()
                }
                
                file_path = save_element_data(folder_path, optimized_data)
                
                return {
                    'success': True,
                    'folder_path': folder_path,
                    'file_path': file_path,
                    'optimization_result': optimization_result
                }
            else:
                print_warning("Nenhum seletor pôde ser otimizado")
                return {
                    'success': False,
                    'message': 'Nenhum seletor válido encontrado para otimização'
                }
                
        except Exception as e:
            print_error(f"Erro durante otimização: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': f"Erro durante otimização: {str(e)}"
            }