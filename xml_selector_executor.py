"""
Executor de Seletores XML para elementos UI
Versão 1.0 - Implementação funcional de seletores XML executáveis

Este módulo implementa um executor robusto que consegue interpretar e executar
seletores XML para encontrar elementos UI usando uiautomation.
"""
import xml.etree.ElementTree as ET
import time
import uiautomation as auto
from utils import print_info, print_error, print_success, print_warning

class XMLSelectorExecutor:
    """
    Executor de seletores XML funcionais para elementos UI
    
    Esta classe interpreta seletores XML no formato padronizado e os executa
    usando a biblioteca uiautomation para encontrar elementos reais na interface.
    """
    
    def __init__(self):
        """
        Inicializa o executor
        """
        self.last_execution_report = {}
        self.default_timeout = 5
        
    def execute_selector(self, xml_selector, timeout=None):
        """
        Executa um seletor XML e retorna o elemento encontrado
        
        Args:
            xml_selector (str): Seletor XML no formato padronizado
            timeout (int): Timeout em segundos (padrão: 5)
            
        Returns:
            uiautomation.Control: Elemento encontrado ou None se falhar
        """
        if timeout is None:
            timeout = self.default_timeout
            
        # Limpa relatório anterior
        self.last_execution_report = {
            'success': False,
            'error': None,
            'steps': [],
            'execution_time': 0,
            'selector_used': xml_selector
        }
        
        start_time = time.time()
        
        try:
            # Parse do XML
            root = self._parse_xml_selector(xml_selector)
            if not root:
                return None
                
            # Executa seletor hierarquicamente
            result_element = self._execute_hierarchical_selector(root, timeout)
            
            # Atualiza relatório de sucesso
            execution_time = time.time() - start_time
            self.last_execution_report.update({
                'success': result_element is not None,
                'execution_time': execution_time,
                'element_found': result_element is not None
            })
            
            return result_element
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.last_execution_report.update({
                'success': False,
                'error': str(e),
                'execution_time': execution_time
            })
            print_error(f"Erro ao executar seletor: {str(e)}")
            return None
    
    def _parse_xml_selector(self, xml_selector):
        """
        Faz parse do seletor XML e valida estrutura
        
        Args:
            xml_selector (str): String XML do seletor
            
        Returns:
            xml.etree.ElementTree.Element: Elemento raiz ou None se inválido
        """
        try:
            # Remove espaços em branco e quebras de linha desnecessárias
            cleaned_xml = xml_selector.strip()
            
            # Parse do XML
            root = ET.fromstring(cleaned_xml)
            
            # Valida que é um seletor válido
            if root.tag != 'Selector':
                self.last_execution_report['error'] = "XML deve ter tag raiz 'Selector'"
                return None
            
            self.last_execution_report['steps'].append({
                'step': 'parse_xml',
                'success': True,
                'message': 'XML parseado com sucesso'
            })
            
            return root
            
        except ET.ParseError as e:
            self.last_execution_report['error'] = f"Erro de sintaxe XML: {str(e)}"
            self.last_execution_report['steps'].append({
                'step': 'parse_xml',
                'success': False,
                'error': str(e)
            })
            return None
        except Exception as e:
            self.last_execution_report['error'] = f"Erro inesperado no parse: {str(e)}"
            return None
    
    def _execute_hierarchical_selector(self, selector_root, timeout):
        """
        Executa seletor de forma hierárquica (Window -> Element -> ...)
        
        Args:
            selector_root: Elemento raiz do XML parseado
            timeout: Timeout para operações
            
        Returns:
            uiautomation.Control: Elemento encontrado ou None
        """
        current_element = None
        
        # Processa cada filho do seletor em ordem
        for child in selector_root:
            if child.tag == 'Window':
                current_element = self._find_window(child, timeout)
                if not current_element:
                    self.last_execution_report['steps'].append({
                        'step': 'find_window',
                        'success': False,
                        'criteria': dict(child.attrib),
                        'error': 'Janela não encontrada'
                    })
                    return None
                else:
                    self.last_execution_report['steps'].append({
                        'step': 'find_window',
                        'success': True,
                        'criteria': dict(child.attrib),
                        'found_title': getattr(current_element, 'Name', ''),
                        'found_class': getattr(current_element, 'ClassName', '')
                    })
                    
            elif child.tag == 'Element':
                if current_element is None:
                    # Se não há elemento pai, busca no desktop
                    current_element = auto.GetRootControl()
                    
                current_element = self._find_element(current_element, child, timeout)
                if not current_element:
                    self.last_execution_report['steps'].append({
                        'step': 'find_element',
                        'success': False,
                        'criteria': dict(child.attrib),
                        'error': 'Elemento não encontrado'
                    })
                    return None
                else:
                    self.last_execution_report['steps'].append({
                        'step': 'find_element',
                        'success': True,
                        'criteria': dict(child.attrib),
                        'found_name': getattr(current_element, 'Name', ''),
                        'found_class': getattr(current_element, 'ClassName', ''),
                        'found_type': getattr(current_element, 'ControlTypeName', '')
                    })
            else:
                # Tag desconhecida, adiciona aviso mas continua
                self.last_execution_report['steps'].append({
                    'step': 'unknown_tag',
                    'success': False,
                    'tag': child.tag,
                    'warning': f'Tag desconhecida ignorada: {child.tag}'
                })
        
        return current_element
    
    def _find_window(self, window_criteria, timeout):
        """
        Encontra janela baseada nos critérios especificados
        
        Args:
            window_criteria: Elemento XML com critérios da janela
            timeout: Timeout para busca
            
        Returns:
            uiautomation.Control: Janela encontrada ou None
        """
        criteria = dict(window_criteria.attrib)
        
        # Estratégias de busca de janela em ordem de prioridade
        search_strategies = []
        
        # Estratégia 1: Por título exato
        if 'title' in criteria:
            search_strategies.append(('title_exact', criteria['title']))
            
        # Estratégia 2: Por título parcial (se título muito longo)
        if 'title' in criteria and len(criteria['title']) > 10:
            partial_title = criteria['title'][:min(20, len(criteria['title']))]
            search_strategies.append(('title_partial', partial_title))
            
        # Estratégia 3: Por classe
        if 'class' in criteria:
            search_strategies.append(('class', criteria['class']))
            
        # Estratégia 4: Por AutomationId
        if 'automationId' in criteria:
            search_strategies.append(('automation_id', criteria['automationId']))
        
        end_time = time.time() + timeout
        
        for strategy_name, value in search_strategies:
            while time.time() < end_time:
                try:
                    windows = auto.GetRootControl().GetChildren()
                    
                    for window in windows:
                        if self._window_matches_criteria(window, strategy_name, value):
                            return window
                            
                    time.sleep(0.1)  # Pequena pausa antes de tentar novamente
                    
                except Exception:
                    continue
                    
        return None
    
    def _window_matches_criteria(self, window, strategy_name, value):
        """
        Verifica se janela atende ao critério especificado
        
        Args:
            window: Objeto da janela
            strategy_name: Nome da estratégia ('title_exact', 'title_partial', etc.)
            value: Valor a ser comparado
            
        Returns:
            bool: True se janela atende ao critério
        """
        try:
            if strategy_name == 'title_exact':
                return getattr(window, 'Name', '') == value
                
            elif strategy_name == 'title_partial':
                window_title = getattr(window, 'Name', '')
                return value.lower() in window_title.lower()
                
            elif strategy_name == 'class':
                return getattr(window, 'ClassName', '') == value
                
            elif strategy_name == 'automation_id':
                return getattr(window, 'AutomationId', '') == value
                
        except Exception:
            pass
            
        return False
    
    def _find_element(self, parent_element, element_criteria, timeout):
        """
        Encontra elemento filho baseado nos critérios especificados,
        considerando typedIndex se presente.
        
        Args:
            parent_element: Elemento pai onde buscar
            element_criteria: Elemento XML com critérios do elemento
            timeout: Timeout para busca
            
        Returns:
            uiautomation.Control: Elemento encontrado ou None
        """
        criteria = dict(element_criteria.attrib)
        target_typed_index = -1

        if 'typedIndex' in criteria:
            try:
                target_typed_index = int(criteria['typedIndex'])
                # Remove typedIndex do critério de busca principal, pois ele é aplicado depois
                # É importante fazer uma cópia de criteria aqui se for modificar
            except ValueError:
                self.last_execution_report['steps'].append({
                    'step': 'find_element_error',
                    'success': False,
                    'criteria': dict(element_criteria.attrib),
                    'error': 'typedIndex inválido (não é um número)'
                })
                return None
        
        criteria_for_filtering = criteria.copy()
        if 'typedIndex' in criteria_for_filtering:
            del criteria_for_filtering['typedIndex']

        # Se typedIndex é especificado, precisamos de todos os elementos que correspondem aos outros critérios.
        if target_typed_index >= 0:
            # Usamos _find_by_any_criteria com find_all=True para obter todos os candidatos
            candidate_elements = self._find_by_any_criteria(parent_element, criteria_for_filtering, timeout, find_all=True)

            if candidate_elements and 0 <= target_typed_index < len(candidate_elements):
                return candidate_elements[target_typed_index]
            else:
                num_candidates = len(candidate_elements) if candidate_elements is not None else 0
                self.last_execution_report['steps'].append({
                    'step': 'find_element_typed_index',
                    'success': False,
                    'criteria': dict(element_criteria.attrib), # Log original criteria
                    'error': f'typedIndex {target_typed_index} fora dos limites ou nenhum candidato encontrado ({num_candidates})'
                })
                return None
        else:
            # Lógica original se typedIndex não estiver presente
            # As buscas específicas podem ser mais rápidas se não precisarmos de todos os candidatos
            name_value = criteria_for_filtering.get('name', '') # Use criteria_for_filtering

            if 'automationId' in criteria_for_filtering:
                return self._find_by_automation_id(parent_element, criteria_for_filtering, timeout)

            elif 'className' in criteria_for_filtering and not name_value:
                return self._find_by_class_name(parent_element, criteria_for_filtering, timeout)

            elif 'name' in criteria_for_filtering and 'controlType' in criteria_for_filtering and name_value:
                return self._find_by_name_and_type(parent_element, criteria_for_filtering, timeout)

            elif 'className' in criteria_for_filtering:
                return self._find_by_class_name(parent_element, criteria_for_filtering, timeout)

            else:
                # Busca genérica por qualquer critério disponível (retorna o primeiro)
                return self._find_by_any_criteria(parent_element, criteria_for_filtering, timeout, find_all=False)
    
    def _find_by_automation_id(self, parent, criteria, timeout):
        """
        Busca elemento por AutomationId (método mais robusto)
        """
        automation_id = criteria['automationId']
        control_type = criteria.get('controlType', '')
        
        end_time = time.time() + timeout
        
        while time.time() < end_time:
            try:
                # Busca direta por AutomationId
                element = parent.Control(AutomationId=automation_id)
                
                if element and element.Exists(0):
                    # Verifica ControlType se especificado
                    if control_type and getattr(element, 'ControlTypeName', '') != control_type:
                        continue
                    return element
                    
            except Exception:
                pass
                
            time.sleep(0.1)
            
        return None
    
    def _find_by_name_and_type(self, parent, criteria, timeout):
        """
        Busca elemento por Name e ControlType
        """
        name = criteria['name']
        control_type = criteria['controlType']
        
        end_time = time.time() + timeout
        
        while time.time() < end_time:
            try:
                # Busca por Name e ControlType
                element = parent.Control(Name=name, ControlType=getattr(auto.ControlType, control_type, None))
                
                if element and element.Exists(0):
                    return element
                    
            except Exception:
                pass
                
            time.sleep(0.1)
            
        return None
    
    def _find_by_class_name(self, parent, criteria, timeout):
        """
        Busca elemento por ClassName com contexto de janela melhorado
        """
        class_name = criteria['className']
        control_type = criteria.get('controlType', '')
        
        end_time = time.time() + timeout
        
        while time.time() < end_time:
            try:
                # Método 1: Busca direta por ClassName
                element = parent.Control(ClassName=class_name)
                
                if element and element.Exists(0):
                    # Verifica ControlType se especificado
                    if control_type and getattr(element, 'ControlTypeName', '') != control_type:
                        continue
                    return element
                
                # Método 2: Busca hierárquica para campos Delphi
                if class_name.startswith(('TDB', 'TEdit', 'Tcx')):
                    children = parent.GetChildren()
                    for child in children:
                        if (getattr(child, 'ClassName', '') == class_name and
                            (not control_type or getattr(child, 'ControlTypeName', '') == control_type)):
                            return child
                        
                        # Busca recursiva em containers (TGroupBox, TPanel)
                        if getattr(child, 'ClassName', '').startswith(('TGroup', 'TPanel')):
                            grandchildren = child.GetChildren()
                            for grandchild in grandchildren:
                                if (getattr(grandchild, 'ClassName', '') == class_name and
                                    (not control_type or getattr(grandchild, 'ControlTypeName', '') == control_type)):
                                    return grandchild
                    
            except Exception:
                pass
                
            time.sleep(0.1)
            
        return None
    
    def _find_by_any_criteria(self, parent, criteria, timeout, find_all=False):
        """
        Busca elemento(s) usando qualquer critério disponível.
        Se find_all is True, retorna uma lista de todos os elementos correspondentes.
        Caso contrário, retorna o primeiro elemento correspondente.
        """
        end_time = time.time() + timeout
        found_elements = []
        
        # Loop de tentativas com timeout
        current_try_time = time.time()
        while current_try_time < end_time:
            try:
                children = parent.GetChildren() # Obter filhos dentro do loop de tentativa
                
                # Itera sobre os filhos uma vez por tentativa de GetChildren()
                elements_in_current_pass = []
                for child in children:
                    if self._element_matches_criteria(child, criteria.copy()): # Usa copia de criteria
                        if find_all:
                            elements_in_current_pass.append(child)
                        else:
                            return child # Retorna o primeiro encontrado imediatamente se não for find_all
                
                if find_all:
                    # Se find_all, acumula os resultados desta passagem e continua buscando até o timeout
                    # para garantir que todos os elementos que podem aparecer dinamicamente sejam capturados.
                    # No entanto, para typedIndex, geralmente queremos os elementos presentes em um snapshot.
                    # Para o caso de typedIndex, a busca é feita uma vez (find_all=true), e o resultado é usado.
                    # A lógica de timeout aqui é mais para encontrar o *primeiro* elemento se não for find_all.
                    # Se estamos em modo find_all, e esta é a chamada de _find_element para typedIndex,
                    # o chamador ( _find_element) vai pegar o resultado e não vai chamar de novo em loop.
                    # Portanto, retornar elements_in_current_pass aqui é o correto para find_all.
                    return elements_in_current_pass # Retorna o que foi encontrado nesta passagem

                # Se não é find_all e nada foi retornado no loop de filhos, tenta novamente após pausa

            except Exception:
                # Ignora erros durante a busca de filhos, pode tentar novamente
                pass # Permite que o loop de timeout continue
            
            time.sleep(0.1) # Pausa antes da próxima tentativa
            current_try_time = time.time() # Atualiza o tempo atual para o loop

        return found_elements if find_all else None # Retorna lista vazia ou None após timeout
    
    def _element_matches_criteria(self, element, criteria):
        """
        Verifica se elemento atende a todos os critérios especificados
        
        Args:
            element: Elemento a ser verificado
            criteria: Dicionário com critérios
            
        Returns:
            bool: True se elemento atende a todos os critérios
        """
        try:
            for key, value in criteria.items():
                if key == 'automationId':
                    if getattr(element, 'AutomationId', '') != value:
                        return False
                elif key == 'name':
                    if getattr(element, 'Name', '') != value:
                        return False
                elif key == 'className':
                    if getattr(element, 'ClassName', '') != value:
                        return False
                elif key == 'controlType':
                    if getattr(element, 'ControlTypeName', '') != value:
                        return False
                elif key == 'accessibleName':
                    try:
                        legacy_pattern = element.GetLegacyIAccessiblePattern()
                        if legacy_pattern:
                            if getattr(legacy_pattern, 'Name', '') != value:
                                return False
                        else: # Pattern not supported by this element
                            return False
                    except Exception: # Error getting pattern or property
                        return False
                        
            return True
            
        except Exception:
            return False
    
    def get_execution_report(self):
        """
        Retorna relatório detalhado da última execução
        
        Returns:
            dict: Relatório com detalhes da execução
        """
        return self.last_execution_report.copy()
    
    def validate_selector(self, xml_selector, expected_element_info=None, timeout=None):
        """
        Valida se um seletor XML consegue encontrar o elemento esperado
        
        Args:
            xml_selector (str): Seletor XML para testar
            expected_element_info (dict): Informações esperadas do elemento (opcional)
            timeout (int): Timeout para teste
            
        Returns:
            dict: Resultado da validação
        """
        result = {
            'valid': False,
            'element_found': False,
            'matches_expected': False,
            'execution_time': 0,
            'errors': []
        }
        
        start_time = time.time()
        
        try:
            # Executa seletor
            found_element = self.execute_selector(xml_selector, timeout)
            result['execution_time'] = time.time() - start_time
            
            if found_element:
                result['element_found'] = True
                result['valid'] = True
                
                # Se há informações esperadas, compara
                if expected_element_info:
                    result['matches_expected'] = self._compare_element_info(
                        found_element, expected_element_info
                    )
                else:
                    result['matches_expected'] = True
                    
            else:
                result['errors'].append("Elemento não encontrado")
                
        except Exception as e:
            result['errors'].append(f"Erro durante validação: {str(e)}")
            result['execution_time'] = time.time() - start_time
            
        return result
    
    def _compare_element_info(self, found_element, expected_info):
        """
        Compara elemento encontrado com informações esperadas
        
        Args:
            found_element: Elemento encontrado
            expected_info: Informações esperadas
            
        Returns:
            bool: True se elemento corresponde ao esperado
        """
        try:
            # Compara propriedades principais
            if 'automation_id' in expected_info:
                if getattr(found_element, 'AutomationId', '') != expected_info['automation_id']:
                    return False
                    
            if 'name' in expected_info:
                if getattr(found_element, 'Name', '') != expected_info['name']:
                    return False
                    
            if 'class_name' in expected_info:
                if getattr(found_element, 'ClassName', '') != expected_info['class_name']:
                    return False
                    
            if 'control_type' in expected_info:
                if getattr(found_element, 'ControlTypeName', '') != expected_info['control_type']:
                    return False
                    
            return True
            
        except Exception:
            return False
    
    def execute_click_action(self, xml_selector, action_type="click", timeout=None):
        """
        Executa ação de clique no elemento encontrado pelo seletor
        
        Args:
            xml_selector (str): Seletor XML para encontrar o elemento
            action_type (str): Tipo de ação ("click", "double_click", "right_click")
            timeout (int): Timeout para encontrar elemento
            
        Returns:
            dict: Resultado da execução da ação
        """
        print_info(f"Executando ação '{action_type}' via seletor XML...")
        
        start_time = time.time()
        
        try:
            # 1. Encontra o elemento
            element = self.execute_selector(xml_selector, timeout)
            
            if not element:
                return {
                    'success': False,
                    'error': 'Elemento não encontrado pelo seletor',
                    'execution_time': time.time() - start_time
                }
            
            print_success("✓ Elemento encontrado! Executando ação...")
            
            # 2. Executa ação baseada no tipo
            if action_type == "click":
                result = self._perform_click(element)
            elif action_type == "double_click":
                result = self._perform_double_click(element)
            elif action_type == "right_click":
                result = self._perform_right_click(element)
            else:
                return {
                    'success': False,
                    'error': f'Tipo de ação não suportado: {action_type}',
                    'execution_time': time.time() - start_time
                }
            
            result['execution_time'] = time.time() - start_time
            result['element_info'] = {
                'name': getattr(element, 'Name', ''),
                'automation_id': getattr(element, 'AutomationId', ''),
                'control_type': getattr(element, 'ControlTypeName', '')
            }
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro ao executar ação: {str(e)}',
                'execution_time': time.time() - start_time
            }
    
    def _perform_click(self, element):
        """
        Executa clique no elemento usando múltiplos métodos
        
        Args:
            element: Elemento UI Automation
            
        Returns:
            dict: Resultado da execução do clique
        """
        try:
            print_info("Tentando clique via InvokePattern...")
            
            # Método 1: InvokePattern (mais robusto e recomendado)
            if hasattr(element, 'GetInvokePattern'):
                try:
                    invoke_pattern = element.GetInvokePattern()
                    if invoke_pattern:
                        invoke_pattern.Invoke()
                        print_success("✓ Clique executado via InvokePattern")
                        return {
                            'success': True,
                            'method': 'InvokePattern',
                            'message': 'Clique executado via padrão de invocação (método recomendado)'
                        }
                except Exception as e:
                    print_warning(f"InvokePattern falhou: {str(e)}")
            
            print_info("InvokePattern não disponível. Tentando clique direto...")
            
            # Método 2: Clique direto do uiautomation
            try:
                element.Click()
                print_success("✓ Clique executado via método direto")
                return {
                    'success': True,
                    'method': 'Direct Click',
                    'message': 'Clique executado via método direto do elemento'
                }
            except Exception as e:
                print_warning(f"Clique direto falhou: {str(e)}")
            
            print_info("Tentando clique por coordenadas...")
            
            # Método 3: Clique por coordenadas (fallback)
            try:
                import win32api, win32con
                
                rect = element.BoundingRectangle
                if rect:
                    center_x = rect.left + (rect.right - rect.left) // 2
                    center_y = rect.top + (rect.bottom - rect.top) // 2
                    
                    # Move mouse para o centro do elemento
                    win32api.SetCursorPos((center_x, center_y))
                    time.sleep(0.1)  # Pequena pausa
                    
                    # Executa clique
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
                    
                    print_success(f"✓ Clique executado por coordenadas ({center_x}, {center_y})")
                    return {
                        'success': True,
                        'method': 'Coordinate Click',
                        'position': (center_x, center_y),
                        'message': f'Clique executado por coordenadas na posição ({center_x}, {center_y})'
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Não foi possível obter coordenadas do elemento'
                    }
                    
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Clique por coordenadas falhou: {str(e)}'
                }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro geral durante clique: {str(e)}'
            }
    
    def _perform_double_click(self, element):
        """
        Executa clique duplo no elemento
        
        Args:
            element: Elemento UI Automation
            
        Returns:
            dict: Resultado da execução do clique duplo
        """
        try:
            import win32api, win32con
            
            rect = element.BoundingRectangle
            if rect:
                center_x = rect.left + (rect.right - rect.left) // 2
                center_y = rect.top + (rect.bottom - rect.top) // 2
                
                # Move mouse para o centro do elemento
                win32api.SetCursorPos((center_x, center_y))
                time.sleep(0.1)
                
                # Executa clique duplo
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
                time.sleep(0.05)  # Pequena pausa entre cliques
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
                
                print_success(f"✓ Clique duplo executado em ({center_x}, {center_y})")
                return {
                    'success': True,
                    'method': 'Double Click',
                    'position': (center_x, center_y),
                    'message': f'Clique duplo executado na posição ({center_x}, {center_y})'
                }
            else:
                return {
                    'success': False,
                    'error': 'Não foi possível obter coordenadas para clique duplo'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro durante clique duplo: {str(e)}'
            }
    
    def _perform_right_click(self, element):
        """
        Executa clique direito no elemento
        
        Args:
            element: Elemento UI Automation
            
        Returns:
            dict: Resultado da execução do clique direito
        """
        try:
            import win32api, win32con
            
            rect = element.BoundingRectangle
            if rect:
                center_x = rect.left + (rect.right - rect.left) // 2
                center_y = rect.top + (rect.bottom - rect.top) // 2
                
                # Move mouse para o centro do elemento
                win32api.SetCursorPos((center_x, center_y))
                time.sleep(0.1)
                
                # Executa clique direito
                win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0)
                win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0)
                
                print_success(f"✓ Clique direito executado em ({center_x}, {center_y})")
                return {
                    'success': True,
                    'method': 'Right Click',
                    'position': (center_x, center_y),
                    'message': f'Clique direito executado na posição ({center_x}, {center_y})'
                }
            else:
                return {
                    'success': False,
                    'error': 'Não foi possível obter coordenadas para clique direito'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro durante clique direito: {str(e)}'
            }