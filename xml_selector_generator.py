"""
Gerador de Seletores XML robustos para elementos UI
Versão 2 - Com múltiplas estratégias de seleção e suporte para clique relativo
"""
import xml.etree.ElementTree as ET
import uiautomation as auto

class XMLSelectorGenerator:
    """
    Gera seletores XML estratégicos e robustos para elementos UI
    
    Esta classe implementa múltiplas estratégias de seleção para garantir
    que elementos possam ser encontrados mesmo quando a UI muda.
    
    Suporta também geração de seletores para clique relativo, permitindo
    clicar em posições relativas a elementos âncora.
    """
    
    def __init__(self):
        """
        Inicializa o gerador com estratégias ordenadas por robustez
        
        As estratégias são aplicadas em ordem, da mais robusta para a menos robusta:
        1. AutomationId (mais estável)
        2. Name + Type (boa para elementos com texto fixo)
        3. Class + Index (útil quando outros atributos não existem)
        4. Caminho hierárquico (quando precisa contexto)
        5. Atributos parciais (para elementos dinâmicos)
        """
        self.selector_strategies = [
            self._strategy_automation_id,
            self._strategy_name_and_type,
            self._strategy_class_and_index,
            self._strategy_hierarchical_path,
            self._strategy_partial_attributes
        ]
    
    def generate_robust_selector(self, element):
        """
        Gera múltiplos seletores XML em ordem de robustez/confiabilidade
        
        Args:
            element: Elemento UI Automation a ser processado
            
        Returns:
            list: Lista de seletores XML do mais confiável para o menos confiável
        """
        selectors = []
        
        # Coleta informações do elemento e seus ancestrais
        element_info = self._extract_element_info(element)
        parent_chain = self._build_parent_chain(element)
        
        # Aplica cada estratégia de seleção
        for strategy in self.selector_strategies:
            try:
                result = strategy(element_info, parent_chain)
                if result:
                    # Se a estratégia retornar uma lista, adiciona todos os seletores
                    if isinstance(result, list):
                        for selector in result:
                            if selector and selector not in selectors:
                                selectors.append(selector)
                    else:
                        # Se retornar um único seletor
                        if result not in selectors:
                            selectors.append(result)
            except Exception as e:
                # Continua com próxima estratégia se houver erro
                continue
        
        # Adiciona seletor de emergência (coordenadas + janela)
        emergency_selector = self._strategy_emergency_fallback(element_info)
        if emergency_selector:
            selectors.append(emergency_selector)
        
        return selectors
    
    def generate_executable_selectors(self, element):
        """
        Gera seletores XML executáveis e funcionais
        
        Esta versão produz XML limpo e válido que pode ser executado
        pelo XMLSelectorExecutor.
        
        Args:
            element: Elemento UI Automation a ser processado
            
        Returns:
            list: Lista de seletores XML executáveis
        """
        selectors = []
        
        # Coleta informações do elemento e seus ancestrais
        element_info = self._extract_element_info(element)
        parent_chain = self._build_parent_chain(element)
        
        # Estratégias executáveis em ordem de robustez
        executable_strategies = [
            self._executable_strategy_automation_id,
            self._executable_strategy_name_and_type,
            self._executable_strategy_class_name,
            self._executable_strategy_hierarchical
        ]
        
        for strategy in executable_strategies:
            try:
                result = strategy(element_info, parent_chain)
                if result:
                    if isinstance(result, list):
                        selectors.extend(result)
                    else:
                        selectors.append(result)
            except Exception:
                continue
        
        return selectors
    
    def _extract_element_info(self, element):
        """
        Extrai todas as informações relevantes do elemento
        
        Args:
            element: Elemento UI Automation
            
        Returns:
            dict: Dicionário com todas as propriedades do elemento
        """
        try:
            # Obtém retângulo delimitador de forma segura
            rect = getattr(element, 'BoundingRectangle', None)
            
            return {
                'automation_id': getattr(element, 'AutomationId', '') or '',
                'name': getattr(element, 'Name', '') or '',
                'class_name': getattr(element, 'ClassName', '') or '',
                'control_type': getattr(element, 'ControlTypeName', '') or '',
                'localized_control_type': getattr(element, 'LocalizedControlType', '') or '',
                'framework_id': getattr(element, 'FrameworkId', '') or '',
                'process_id': getattr(element, 'ProcessId', 0),
                'runtime_id': self._safe_get_runtime_id(element),
                'is_enabled': getattr(element, 'IsEnabled', True),
                'is_visible': not getattr(element, 'IsOffscreen', False),
                'bounding_rect': {
                    'left': rect.left if rect else 0,
                    'top': rect.top if rect else 0,
                    'right': rect.right if rect else 0,
                    'bottom': rect.bottom if rect else 0,
                    'width': (rect.right - rect.left) if rect else 0,
                    'height': (rect.bottom - rect.top) if rect else 0
                },
                'patterns': self._get_available_patterns(element),
                'parent_window': self._get_parent_window_info(element)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _safe_get_runtime_id(self, element):
        """
        Obtém RuntimeId de forma segura
        
        RuntimeId pode não estar disponível em todos os elementos
        
        Args:
            element: Elemento UI Automation
            
        Returns:
            list: Lista com RuntimeId ou lista vazia se não disponível
        """
        try:
            runtime_id = getattr(element, 'RuntimeId', None)
            if runtime_id:
                return list(runtime_id)
            return []
        except Exception:
            return []
    
    def _build_parent_chain(self, element, max_depth=5):
        """
        Constrói cadeia de elementos pai até a janela principal
        
        Args:
            element: Elemento inicial
            max_depth: Profundidade máxima para percorrer (evita loops infinitos)
            
        Returns:
            list: Lista de dicionários com informações dos pais
        """
        chain = []
        current = element
        depth = 0
        
        try:
            while current and depth < max_depth:
                parent = current.GetParentControl()
                if not parent or parent == current:
                    break
                
                # Coleta informações do pai
                chain.append({
                    'automation_id': getattr(parent, 'AutomationId', '') or '',
                    'name': getattr(parent, 'Name', '') or '',
                    'class_name': getattr(parent, 'ClassName', '') or '',
                    'control_type': getattr(parent, 'ControlTypeName', '') or '',
                    'index': self._get_sibling_index(parent)
                })
                
                current = parent
                depth += 1
                
        except Exception:
            pass
        
        return chain
    
    def _get_sibling_index(self, element):
        """
        Obtém índice do elemento entre seus irmãos do mesmo tipo
        
        Útil quando múltiplos elementos têm as mesmas propriedades
        
        Args:
            element: Elemento para obter índice
            
        Returns:
            int: Índice entre irmãos do mesmo tipo
        """
        try:
            parent = element.GetParentControl()
            if not parent:
                return 0
            
            siblings = parent.GetChildren()
            if not siblings:
                return 0
            
            element_control_type = getattr(element, 'ControlTypeName', '')
            same_type_count = 0
            
            for sibling in siblings:
                sibling_type = getattr(sibling, 'ControlTypeName', '')
                if sibling_type == element_control_type:
                    if sibling == element:
                        return same_type_count
                    same_type_count += 1
            
            return 0
        except Exception:
            return 0
    
    def _get_available_patterns(self, element):
        """
        Lista padrões de automação suportados pelo elemento
        
        Args:
            element: Elemento UI Automation
            
        Returns:
            list: Lista de nomes de padrões suportados
        """
        patterns = []
        pattern_methods = [
            'GetInvokePattern', 'GetValuePattern', 'GetTextPattern', 'GetTogglePattern',
            'GetSelectionPattern', 'GetSelectionItemPattern', 'GetExpandCollapsePattern',
            'GetScrollPattern', 'GetGridPattern', 'GetTablePattern', 'GetWindowPattern'
        ]
        
        try:
            for method_name in pattern_methods:
                if hasattr(element, method_name):
                    try:
                        pattern = getattr(element, method_name)()
                        if pattern:
                            patterns.append(method_name.replace('Get', '').replace('Pattern', '') + 'Pattern')
                    except:
                        pass
        except Exception:
            pass
        
        return patterns
    
    def _get_parent_window_info(self, element):
        """
        Obtém informações da janela pai
        
        Navega pela hierarquia até encontrar uma WindowControl
        
        Args:
            element: Elemento inicial
            
        Returns:
            dict: Informações da janela ou None se não encontrar
        """
        try:
            current = element
            max_depth = 10
            depth = 0
            
            while current and depth < max_depth:
                control_type = getattr(current, 'ControlTypeName', '')
                if control_type in ['WindowControl', 'Window']:
                    return {
                        'title': getattr(current, 'Name', '') or '',
                        'class_name': getattr(current, 'ClassName', '') or '',
                        'automation_id': getattr(current, 'AutomationId', '') or '',
                        'process_id': getattr(current, 'ProcessId', 0)
                    }
                try:
                    current = current.GetParentControl()
                    if not current:
                        break
                    depth += 1
                except:
                    break
        except Exception:
            pass
        return None
    
    def _strategy_automation_id(self, element_info, parent_chain):
        """
        Estratégia mais robusta: AutomationId com múltiplas variações
        
        Gera:
        1. Seletor com janela (mais específico)
        2. Seletor sem janela (mais flexível)
        3. Seletor com contexto de pai (se disponível)
        
        Args:
            element_info: Informações do elemento
            parent_chain: Cadeia de elementos pai
            
        Returns:
            list: Lista de seletores ou None se AutomationId não existir
        """
        automation_id = element_info.get('automation_id')
        if not automation_id:
            return None
        
        selectors = []
        control_type = element_info.get('control_type', '*')
        window_info = element_info.get('parent_window')
        
        # Seletor 1: Com janela (MAIS ROBUSTO)
        if window_info and window_info.get('title'):
            selector_with_window = f"""
<!-- Seletor por AutomationId com Janela (MAIS ROBUSTO) -->
<Selector>
    <Window title="{window_info['title']}" class="{window_info.get('class_name', '*')}" />
    <Element automationId="{automation_id}" controlType="{control_type}" />
</Selector>"""
            selectors.append(selector_with_window)
        
        # Seletor 2: Sem janela (MAIS FLEXÍVEL)
        selector_without_window = f"""
<!-- Seletor por AutomationId Direto (FLEXÍVEL) -->
<Selector>
    <Element automationId="{automation_id}" controlType="{control_type}" />
</Selector>"""
        selectors.append(selector_without_window)
        
        # Seletor 3: Com hierarquia de pai se disponível
        if parent_chain and len(parent_chain) > 0:
            parent = parent_chain[0]
            if parent.get('automation_id'):
                selector_with_parent = f"""
<!-- Seletor por AutomationId com Contexto de Pai -->
<Selector>
    <Element automationId="{parent['automation_id']}" />
    <Element automationId="{automation_id}" controlType="{control_type}" />
</Selector>"""
                selectors.append(selector_with_parent)
        
        # Retorna lista de seletores ou o primeiro se houver apenas um
        return selectors[0] if len(selectors) == 1 else selectors
    
    def _strategy_name_and_type(self, element_info, parent_chain):
        """
        Estratégia por Name + ControlType
        
        Útil para elementos com texto fixo como botões e labels
        
        Args:
            element_info: Informações do elemento
            parent_chain: Cadeia de elementos pai
            
        Returns:
            str: Seletor XML ou None
        """
        name = element_info.get('name')
        control_type = element_info.get('control_type')
        
        if not name or not control_type:
            return None
        
        window_info = element_info.get('parent_window')
        if window_info and window_info.get('title'):
            return f"""
<!-- Seletor por Name + ControlType -->
<Selector>
    <Window title="{window_info['title']}" />
    <Element name="{name}" controlType="{control_type}" />
</Selector>"""
        else:
            return f"""
<!-- Seletor por Name + ControlType Simples -->
<Selector>
    <Element name="{name}" controlType="{control_type}" />
</Selector>"""
    
    def _strategy_class_and_index(self, element_info, parent_chain):
        """
        Estratégia por ClassName + Índice
        
        Útil quando AutomationId e Name não estão disponíveis
        
        Args:
            element_info: Informações do elemento
            parent_chain: Cadeia de elementos pai
            
        Returns:
            str: Seletor XML ou None
        """
        class_name = element_info.get('class_name')
        control_type = element_info.get('control_type')
        
        if not class_name:
            return None
        
        # Tenta usar informação do pai para criar seletor mais específico
        if parent_chain and len(parent_chain) > 0:
            parent = parent_chain[0]
            parent_selector = ""
            
            if parent.get('automation_id'):
                parent_selector = f'automationId="{parent["automation_id"]}"'
            elif parent.get('name'):
                parent_selector = f'name="{parent["name"]}"'
            elif parent.get('class_name'):
                parent_selector = f'className="{parent["class_name"]}"'
            
            if parent_selector:
                return f"""
<!-- Seletor por Hierarquia com ClassName -->
<Selector>
    <Element {parent_selector} controlType="{parent.get('control_type', '*')}" />
    <Element className="{class_name}" controlType="{control_type}" />
</Selector>"""
        
        return f"""
<!-- Seletor por ClassName -->
<Selector>
    <Element className="{class_name}" controlType="{control_type}" />
</Selector>"""
    
    def _strategy_hierarchical_path(self, element_info, parent_chain):
        """
        Estratégia de caminho hierárquico completo
        
        Cria um caminho desde a janela até o elemento
        
        Args:
            element_info: Informações do elemento
            parent_chain: Cadeia de elementos pai
            
        Returns:
            str: Seletor XML ou None
        """
        if not parent_chain or len(parent_chain) < 2:
            return None
        
        selector_parts = []
        window_info = element_info.get('parent_window')
        
        # Adiciona janela se disponível
        if window_info and window_info.get('title'):
            selector_parts.append(f'<Window title="{window_info["title"]}" />')
        
        # Adiciona elementos pai em ordem reversa (do mais alto para o mais baixo)
        # Limita a 3 níveis para não ficar muito específico
        for parent in reversed(parent_chain[:3]):
            attributes = []
            
            if parent.get('automation_id'):
                attributes.append(f'automationId="{parent["automation_id"]}"')
            elif parent.get('name'):
                attributes.append(f'name="{parent["name"]}"')
            elif parent.get('class_name'):
                attributes.append(f'className="{parent["class_name"]}"')
            
            if parent.get('control_type'):
                attributes.append(f'controlType="{parent["control_type"]}"')
            
            # Adiciona índice apenas se for maior que 0
            if parent.get('index', 0) > 0:
                attributes.append(f'index="{parent["index"]}"')
            
            if attributes:
                selector_parts.append(f'<Element {" ".join(attributes)} />')
        
        # Adiciona o elemento target
        target_attrs = []
        if element_info.get('automation_id'):
            target_attrs.append(f'automationId="{element_info["automation_id"]}"')
        elif element_info.get('name'):
            target_attrs.append(f'name="{element_info["name"]}"')
        elif element_info.get('class_name'):
            target_attrs.append(f'className="{element_info["class_name"]}"')
        
        if element_info.get('control_type'):
            target_attrs.append(f'controlType="{element_info["control_type"]}"')
        
        if target_attrs:
            selector_parts.append(f'<Element {" ".join(target_attrs)} />')
        
        if len(selector_parts) > 1:
            return f"""
<!-- Seletor Hierárquico Completo -->
<Selector>
    {chr(10).join(f'    {part}' for part in selector_parts)}
</Selector>"""
        
        return None
    
    def _strategy_partial_attributes(self, element_info, parent_chain):
        """
        Estratégia com atributos parciais/contains
        
        Útil para elementos com texto dinâmico
        
        Args:
            element_info: Informações do elemento
            parent_chain: Cadeia de elementos pai
            
        Returns:
            str: Seletor XML ou None
        """
        name = element_info.get('name', '')
        control_type = element_info.get('control_type')
        
        # Nome muito curto não é confiável para busca parcial
        if len(name) < 3:
            return None
        
        # Usa parte do nome para seleção mais flexível
        # Limita a 20 caracteres para evitar textos muito longos
        partial_name = name[:min(len(name), 20)]
        
        return f"""
<!-- Seletor por Nome Parcial -->
<Selector>
    <Element nameContains="{partial_name}" controlType="{control_type}" />
</Selector>"""
    
    def _strategy_emergency_fallback(self, element_info):
        """
        Estratégia de emergência usando coordenadas
        
        Último recurso quando nenhum outro método funciona
        
        Args:
            element_info: Informações do elemento
            
        Returns:
            str: Seletor XML ou None
        """
        rect = element_info.get('bounding_rect')
        window_info = element_info.get('parent_window')
        
        if not rect or not window_info:
            return None
        
        # Calcula centro do elemento
        center_x = rect['left'] + rect['width'] // 2
        center_y = rect['top'] + rect['height'] // 2
        
        return f"""
<!-- Seletor de Emergência por Coordenadas (MENOS ROBUSTO) -->
<Selector>
    <Window title="{window_info.get('title', '*')}" />
    <Element coordinateX="{center_x}" coordinateY="{center_y}" tolerance="5" />
    <!-- Região: x={rect['left']}, y={rect['top']}, w={rect['width']}, h={rect['height']} -->
</Selector>"""
    
    def generate_relative_click_selectors(self, anchor_element_info, relative_click_info):
        """
        Gera seletores XML para clique relativo a um elemento âncora
        
        Cria múltiplos seletores que permitem clicar em uma posição
        relativa a um elemento âncora, independente de resolução.
        
        Args:
            anchor_element_info: Informações do elemento âncora
            relative_click_info: Informações do clique relativo
            
        Returns:
            list: Lista de seletores XML para clique relativo
        """
        selectors = []
        
        # Extrai informações necessárias
        anchor_id = anchor_element_info.get('automation_id')
        anchor_name = anchor_element_info.get('name')
        anchor_class = anchor_element_info.get('class_name')
        anchor_type = anchor_element_info.get('control_type')
        window_info = anchor_element_info.get('window_info', {})
        
        # Informações do clique relativo
        anchor_offset = relative_click_info.get('anchor_relative', {})
        window_offset = relative_click_info.get('window_relative', {})
        
        # Seletor 1: Clique relativo ao âncora usando AutomationId (MAIS ROBUSTO)
        if anchor_id and anchor_offset:
            selector = f"""
<!-- Seletor de Clique Relativo por AutomationId do Âncora (MAIS ROBUSTO) -->
<Selector>
    <Window title="{window_info.get('title', '*')}" />
    <AnchorElement automationId="{anchor_id}" controlType="{anchor_type}" />
    <RelativeClick offsetX="{anchor_offset.get('offset_x', 0)}" offsetY="{anchor_offset.get('offset_y', 0)}" />
    <!-- {anchor_offset.get('description', '')} -->
</Selector>"""
            selectors.append(selector)
        
        # Seletor 2: Clique relativo usando percentual da janela (INDEPENDENTE DE RESOLUÇÃO)
        if window_offset and window_info.get('title'):
            selector = f"""
<!-- Seletor de Clique Relativo por Percentual da Janela (INDEPENDENTE DE RESOLUÇÃO) -->
<Selector>
    <Window title="{window_info.get('title')}" />
    <WindowRelativeClick percentX="{window_offset.get('percent_x', 0)}" percentY="{window_offset.get('percent_y', 0)}" />
    <!-- {window_offset.get('description', '')} -->
</Selector>"""
            selectors.append(selector)
        
        # Seletor 3: Clique relativo ao âncora usando Name
        if anchor_name and anchor_offset:
            selector = f"""
<!-- Seletor de Clique Relativo por Name do Âncora -->
<Selector>
    <Window title="{window_info.get('title', '*')}" />
    <AnchorElement name="{anchor_name}" controlType="{anchor_type}" />
    <RelativeClick offsetX="{anchor_offset.get('offset_x', 0)}" offsetY="{anchor_offset.get('offset_y', 0)}" />
</Selector>"""
            selectors.append(selector)
        
        # Seletor 4: Clique com offset da janela em pixels (para casos específicos)
        if window_offset:
            selector = f"""
<!-- Seletor de Clique por Offset Absoluto da Janela -->
<Selector>
    <Window title="{window_info.get('title', '*')}" />
    <WindowClick offsetX="{window_offset.get('offset_x', 0)}" offsetY="{window_offset.get('offset_y', 0)}" />
    <!-- Posição fixa em pixels desde o canto superior esquerdo da janela -->
</Selector>"""
            selectors.append(selector)
        
        # Seletor 5: Combinação hierárquica com âncora
        if anchor_id and anchor_offset and anchor_element_info.get('parent_info'):
            parent_info = anchor_element_info.get('parent_info', {})
            selector = f"""
<!-- Seletor de Clique Relativo com Contexto Hierárquico -->
<Selector>
    <Window title="{window_info.get('title', '*')}" />
    <Element automationId="{parent_info.get('automation_id', '*')}" controlType="{parent_info.get('control_type', '*')}" />
    <AnchorElement automationId="{anchor_id}" />
    <RelativeClick offsetX="{anchor_offset.get('offset_x', 0)}" offsetY="{anchor_offset.get('offset_y', 0)}" />
</Selector>"""
            selectors.append(selector)
        
        # Seletor 6: Fallback com coordenadas absolutas
        absolute_pos = relative_click_info.get('absolute_position', {})
        if absolute_pos:
            selector = f"""
<!-- Seletor de Emergência com Coordenadas Absolutas (MENOS ROBUSTO) -->
<Selector>
    <Window title="{window_info.get('title', '*')}" />
    <AbsoluteClick x="{absolute_pos.get('x', 0)}" y="{absolute_pos.get('y', 0)}" />
    <!-- Coordenadas absolutas da tela - usar apenas como último recurso -->
</Selector>"""
            selectors.append(selector)
        
        return selectors
    
    # ================== MÉTODOS DE ESTRATÉGIA EXECUTÁVEL ==================
    
    def _executable_strategy_automation_id(self, element_info, parent_chain):
        """
        Gera seletor executável por AutomationId
        
        Args:
            element_info: Informações do elemento
            parent_chain: Cadeia de elementos pai
            
        Returns:
            list: Lista de seletores XML executáveis
        """
        automation_id = element_info.get('automation_id')
        if not automation_id:
            return []
        
        selectors = []
        control_type = element_info.get('control_type', '')
        window_info = element_info.get('parent_window')
        
        # Seletor 1: Com janela específica (mais robusto)
        if window_info and window_info.get('title'):
            selector = f'<Selector><Window title="{self._escape_xml(window_info["title"])}" /><Element automationId="{self._escape_xml(automation_id)}" controlType="{control_type}" /></Selector>'
            selectors.append(selector)
        
        # Seletor 2: Sem janela (mais flexível)
        selector = f'<Selector><Element automationId="{self._escape_xml(automation_id)}" controlType="{control_type}" /></Selector>'
        selectors.append(selector)
        
        return selectors
    
    def _executable_strategy_name_and_type(self, element_info, parent_chain):
        """
        Gera seletor executável por Name + ControlType
        
        Args:
            element_info: Informações do elemento
            parent_chain: Cadeia de elementos pai
            
        Returns:
            str: Seletor XML executável ou None
        """
        name = element_info.get('name')
        control_type = element_info.get('control_type')
        
        if not name or not control_type:
            return None
        
        window_info = element_info.get('parent_window')
        
        if window_info and window_info.get('title'):
            return f'<Selector><Window title="{self._escape_xml(window_info["title"])}" /><Element name="{self._escape_xml(name)}" controlType="{control_type}" /></Selector>'
        else:
            return f'<Selector><Element name="{self._escape_xml(name)}" controlType="{control_type}" /></Selector>'
    
    def _executable_strategy_class_name(self, element_info, parent_chain):
        """
        Gera seletor executável por ClassName
        
        Args:
            element_info: Informações do elemento
            parent_chain: Cadeia de elementos pai
            
        Returns:
            str: Seletor XML executável ou None
        """
        class_name = element_info.get('class_name')
        control_type = element_info.get('control_type')
        
        if not class_name:
            return None
        
        window_info = element_info.get('parent_window')
        
        if window_info and window_info.get('title'):
            return f'<Selector><Window title="{self._escape_xml(window_info["title"])}" /><Element className="{self._escape_xml(class_name)}" controlType="{control_type}" /></Selector>'
        else:
            return f'<Selector><Element className="{self._escape_xml(class_name)}" controlType="{control_type}" /></Selector>'
    
    def _executable_strategy_hierarchical(self, element_info, parent_chain):
        """
        Gera seletor executável hierárquico
        
        Args:
            element_info: Informações do elemento
            parent_chain: Cadeia de elementos pai
            
        Returns:
            str: Seletor XML executável ou None
        """
        if not parent_chain or len(parent_chain) == 0:
            return None
        
        # Usa apenas o primeiro pai para simplicidade
        parent = parent_chain[0]
        window_info = element_info.get('parent_window')
        
        # Monta seletor hierárquico
        parts = []
        
        # Adiciona janela se disponível
        if window_info and window_info.get('title'):
            parts.append(f'<Window title="{self._escape_xml(window_info["title"])}" />')
        
        # Adiciona elemento pai
        if parent.get('automation_id'):
            parts.append(f'<Element automationId="{self._escape_xml(parent["automation_id"])}" />')
        elif parent.get('name'):
            parts.append(f'<Element name="{self._escape_xml(parent["name"])}" controlType="{parent.get("control_type", "")}" />')
        elif parent.get('class_name'):
            parts.append(f'<Element className="{self._escape_xml(parent["class_name"])}" />')
        else:
            return None
        
        # Adiciona elemento target
        if element_info.get('automation_id'):
            parts.append(f'<Element automationId="{self._escape_xml(element_info["automation_id"])}" controlType="{element_info.get("control_type", "")}" />')
        elif element_info.get('name'):
            parts.append(f'<Element name="{self._escape_xml(element_info["name"])}" controlType="{element_info.get("control_type", "")}" />')
        elif element_info.get('class_name'):
            parts.append(f'<Element className="{self._escape_xml(element_info["class_name"])}" controlType="{element_info.get("control_type", "")}" />')
        else:
            return None
        
        return f'<Selector>{"".join(parts)}</Selector>'
    
    def _escape_xml(self, text):
        """
        Escapa caracteres especiais para XML
        
        Args:
            text: Texto a ser escapado
            
        Returns:
            str: Texto escapado para XML
        """
        if not isinstance(text, str):
            text = str(text)
        
        # Escapa caracteres especiais XML
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&apos;')
        
        return text