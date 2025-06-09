"""
Gerador de Seletores XML Ultra-Robustos
Versão 1.0 - Sistema blindado contra mudanças de AutomationId e interface

Este módulo implementa algoritmos avançados para gerar seletores XML extremamente
confiáveis que funcionam mesmo quando AutomationId muda entre execuções.
"""
import re
import time
import json
from datetime import datetime
from xml_selector_generator import XMLSelectorGenerator
from xml_selector_executor import XMLSelectorExecutor
from utils import print_info, print_success, print_warning, print_error

class UltraRobustSelectorGenerator:
    """
    Gerador de seletores XML ultra-robustos para automação
    
    Este gerador analisa a estabilidade dos atributos do elemento e gera
    múltiplas estratégias de seleção ordenadas por confiabilidade.
    """
    
    def __init__(self):
        """
        Inicializa o gerador ultra-robusto
        """
        self.base_generator = XMLSelectorGenerator()
        self.executor = XMLSelectorExecutor()
        
        # Pesos de confiabilidade para diferentes atributos
        self.attribute_stability_weights = {
            'name': 0.9,           # Nome geralmente estável
            'control_type': 1.0,   # ControlType sempre estável
            'class_name': 0.8,     # ClassName moderadamente estável
            'automation_id': 0.3,  # AutomationId frequentemente instável
            'localized_control_type': 0.7,
            'framework_id': 0.6,
            'window_title': 0.85,
            'parent_info': 0.8
        }
    
    def generate_ultra_robust_selector(self, element):
        """
        Gera seletor XML ultra-robusto com múltiplas estratégias
        
        Args:
            element: Elemento UI Automation capturado
            
        Returns:
            dict: Seletor robusto com múltiplas estratégias e metadados
        """
        print_info("Gerando seletor XML ultra-robusto...")
        
        start_time = time.time()
        
        try:
            # 1. Extrai informações completas do elemento
            element_info = self.base_generator._extract_element_info(element)
            
            # 2. Analisa estabilidade dos atributos
            stability_analysis = self._analyze_attribute_stability(element_info)
            
            # 3. Constrói contexto hierárquico completo
            full_hierarchy = self._build_full_hierarchy_context(element)
            
            # 4. Gera múltiplas estratégias ordenadas por robustez
            strategies = self._generate_multiple_strategies(element_info, full_hierarchy, stability_analysis)
            
            # 5. Valida e otimiza estratégias
            validated_strategies = self._validate_and_rank_strategies(strategies, element)
            
            # 6. Constrói resultado final
            result = {
                'ultra_robust_selector': self._build_final_xml_selector(validated_strategies),
                'strategies': validated_strategies,
                'stability_analysis': stability_analysis,
                'hierarchy_context': full_hierarchy,
                'generation_metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'generation_time': time.time() - start_time,
                    'reliability_score': self._calculate_overall_reliability(validated_strategies),
                    'recommended_strategy': validated_strategies[0]['name'] if validated_strategies else 'none'
                }
            }
            
            print_success(f"✓ Seletor ultra-robusto gerado com {len(validated_strategies)} estratégias")
            print_info(f"Confiabilidade estimada: {result['generation_metadata']['reliability_score']:.1f}%")
            
            return result
            
        except Exception as e:
            print_error(f"Erro ao gerar seletor ultra-robusto: {str(e)}")
            return None
    
    def _analyze_attribute_stability(self, element_info):
        """
        Analisa estabilidade dos atributos do elemento
        
        Args:
            element_info: Informações extraídas do elemento
            
        Returns:
            dict: Análise de estabilidade de cada atributo
        """
        analysis = {}
        
        for attr_name, base_weight in self.attribute_stability_weights.items():
            attr_value = element_info.get(attr_name, '')
            
            if not attr_value or attr_value == '':
                analysis[attr_name] = {'score': 0.0, 'reason': 'Atributo vazio'}
                continue
            
            # Análise específica por tipo de atributo
            if attr_name == 'automation_id':
                score = self._analyze_automation_id_stability(attr_value)
            elif attr_name == 'name':
                score = self._analyze_name_stability(attr_value)
            elif attr_name == 'class_name':
                score = self._analyze_class_name_stability(attr_value)
            elif attr_name == 'window_title':
                score = self._analyze_window_title_stability(attr_value)
            else:
                score = base_weight
            
            analysis[attr_name] = {
                'score': score,
                'value': str(attr_value),
                'base_weight': base_weight,
                'recommended': score >= 0.7
            }
        
        return analysis
    
    def _analyze_automation_id_stability(self, automation_id):
        """
        Analisa se AutomationId parece estável ou dinâmico
        
        Args:
            automation_id: Valor do AutomationId
            
        Returns:
            float: Score de estabilidade (0.0 a 1.0)
        """
        if not automation_id:
            return 0.0
        
        # Padrões que indicam AutomationId dinâmico (instável)
        dynamic_patterns = [
            r'\d{10,}',           # Timestamps longos
            r'[a-f0-9]{8,}',      # Hashes hexadecimais
            r'_\d+_\d+',          # Coordenadas ou índices
            r'temp_\w+',          # Elementos temporários
            r'generated_\w+',     # Elementos gerados
            r'\w+_[0-9a-f]{6,}'   # Sufixos hex
        ]
        
        # Padrões que indicam AutomationId estável
        stable_patterns = [
            r'^btn_\w+$',         # Botões com prefixo
            r'^txt_\w+$',         # Campos de texto com prefixo
            r'^menu_\w+$',        # Menus com prefixo
            r'^tab_\w+$',         # Abas com prefixo
            r'^\w+_button$',      # Sufixo button
            r'^\w+_field$'        # Sufixo field
        ]
        
        # Verifica padrões dinâmicos
        for pattern in dynamic_patterns:
            if re.search(pattern, automation_id, re.IGNORECASE):
                return 0.1  # Muito instável
        
        # Verifica padrões estáveis
        for pattern in stable_patterns:
            if re.search(pattern, automation_id, re.IGNORECASE):
                return 0.8  # Bastante estável
        
        # AutomationId simples e curto geralmente é mais estável
        if len(automation_id) < 20 and automation_id.isalnum():
            return 0.6
        
        # Padrão padrão
        return 0.3
    
    def _analyze_name_stability(self, name):
        """
        Analisa estabilidade do atributo Name
        
        Args:
            name: Valor do Name
            
        Returns:
            float: Score de estabilidade
        """
        if not name:
            return 0.0
        
        # Names com conteúdo dinâmico são instáveis
        dynamic_indicators = [
            r'\d{2}/\d{2}/\d{4}',  # Datas
            r'\d{2}:\d{2}:\d{2}',  # Horários
            r'\$[\d,]+\.\d{2}',    # Valores monetários
            r'\d+%',               # Percentuais
            r'#\d+',               # IDs ou números
        ]
        
        for pattern in dynamic_indicators:
            if re.search(pattern, name):
                return 0.4  # Nome contém dados dinâmicos
        
        # Names de botões/controles fixos são muito estáveis
        stable_names = [
            'ok', 'cancel', 'cancelar', 'salvar', 'save', 'abrir', 'open',
            'fechar', 'close', 'novo', 'new', 'editar', 'edit', 'excluir',
            'delete', 'imprimir', 'print', 'buscar', 'search', 'ajuda', 'help'
        ]
        
        if name.lower() in stable_names:
            return 0.95  # Nome muito estável
        
        # Names não-numéricos são geralmente estáveis
        if not re.search(r'\d', name):
            return 0.85
        
        return 0.7  # Padrão moderadamente estável
    
    def _analyze_class_name_stability(self, class_name):
        """
        Analisa estabilidade do ClassName
        
        Args:
            class_name: Valor do ClassName
            
        Returns:
            float: Score de estabilidade
        """
        if not class_name:
            return 0.0
        
        # ClassNames com sufixos dinâmicos
        if re.search(r'_\d+$', class_name):
            return 0.3  # Classe com sufixo numérico
        
        # ClassNames de frameworks conhecidos são estáveis
        stable_frameworks = [
            'Button', 'TextBox', 'ComboBox', 'ListBox', 'CheckBox',
            'RadioButton', 'Label', 'Panel', 'GroupBox', 'TabControl'
        ]
        
        for framework in stable_frameworks:
            if framework.lower() in class_name.lower():
                return 0.9
        
        return 0.8  # ClassName geralmente estável
    
    def _analyze_window_title_stability(self, window_title):
        """
        Analisa estabilidade do título da janela
        
        Args:
            window_title: Título da janela
            
        Returns:
            float: Score de estabilidade
        """
        if not window_title:
            return 0.0
        
        # Títulos com informações dinâmicas
        dynamic_patterns = [
            r'\d+%',                    # Percentuais de progresso
            r'\(\d+/\d+\)',            # Contadores
            r'- \d{2}/\d{2}/\d{4}',    # Datas no título
            r'v\d+\.\d+\.\d+',         # Versões específicas
        ]
        
        for pattern in dynamic_patterns:
            if re.search(pattern, window_title):
                return 0.6  # Título contém elementos dinâmicos
        
        # Títulos de aplicação são geralmente estáveis
        return 0.85
    
    def _build_full_hierarchy_context(self, element):
        """
        Constrói contexto hierárquico completo do elemento
        
        Args:
            element: Elemento UI Automation
            
        Returns:
            list: Hierarquia completa até a janela raiz
        """
        hierarchy = []
        current = element
        depth = 0
        max_depth = 8  # Evita loops infinitos
        
        try:
            while current and depth < max_depth:
                # Obtém informações do elemento atual
                element_data = {
                    'level': depth,
                    'automation_id': getattr(current, 'AutomationId', '') or '',
                    'name': getattr(current, 'Name', '') or '',
                    'class_name': getattr(current, 'ClassName', '') or '',
                    'control_type': getattr(current, 'ControlTypeName', '') or '',
                    'localized_control_type': getattr(current, 'LocalizedControlType', '') or '',
                    'framework_id': getattr(current, 'FrameworkId', '') or '',
                    'is_enabled': getattr(current, 'IsEnabled', True),
                    'is_visible': not getattr(current, 'IsOffscreen', False),
                    'sibling_index': self._get_sibling_index_advanced(current),
                    'children_count': self._get_children_count_safe(current)
                }
                
                # Adiciona informações de bounding rectangle
                try:
                    rect = current.BoundingRectangle
                    element_data['bounding_rect'] = {
                        'left': rect.left,
                        'top': rect.top,
                        'width': rect.right - rect.left,
                        'height': rect.bottom - rect.top
                    }
                except:
                    element_data['bounding_rect'] = None
                
                hierarchy.append(element_data)
                
                # Para se chegou na janela raiz
                if element_data['control_type'] in ['WindowControl', 'Window']:
                    break
                
                # Sobe um nível na hierarquia
                try:
                    parent = current.GetParentControl()
                    if not parent or parent == current:
                        break
                    current = parent
                    depth += 1
                except:
                    break
        
        except Exception as e:
            print_warning(f"Erro ao construir hierarquia: {str(e)}")
        
        return list(reversed(hierarchy))  # Retorna da janela para o elemento
    
    def _get_sibling_index_advanced(self, element):
        """
        Obtém índice avançado entre elementos irmãos
        
        Args:
            element: Elemento UI Automation
            
        Returns:
            dict: Informações de índice entre irmãos
        """
        try:
            parent = element.GetParentControl()
            if not parent:
                return {'index': 0, 'total_siblings': 0, 'same_type_index': 0}
            
            siblings = parent.GetChildren()
            if not siblings:
                return {'index': 0, 'total_siblings': 0, 'same_type_index': 0}
            
            element_type = getattr(element, 'ControlTypeName', '')
            same_type_count = 0
            element_index = -1
            same_type_index = -1
            
            for i, sibling in enumerate(siblings):
                sibling_type = getattr(sibling, 'ControlTypeName', '')
                
                if sibling == element:
                    element_index = i
                    same_type_index = same_type_count
                
                if sibling_type == element_type:
                    same_type_count += 1
            
            return {
                'index': element_index,
                'total_siblings': len(siblings),
                'same_type_index': same_type_index,
                'same_type_total': same_type_count
            }
        
        except Exception:
            return {'index': 0, 'total_siblings': 0, 'same_type_index': 0}
    
    def _get_children_count_safe(self, element):
        """
        Conta filhos de forma segura
        
        Args:
            element: Elemento UI Automation
            
        Returns:
            int: Número de filhos
        """
        try:
            children = element.GetChildren()
            return len(children) if children else 0
        except:
            return 0
    
    def _generate_multiple_strategies(self, element_info, hierarchy, stability_analysis):
        """
        Gera múltiplas estratégias de seleção ordenadas por robustez
        
        Args:
            element_info: Informações do elemento
            hierarchy: Contexto hierárquico
            stability_analysis: Análise de estabilidade
            
        Returns:
            list: Lista de estratégias ordenadas por confiabilidade
        """
        strategies = []
        
        # Estratégia 1: Name + ControlType + Hierarquia (mais robusta)
        if stability_analysis.get('name', {}).get('score', 0) >= 0.7:
            strategies.append(self._generate_name_hierarchy_strategy(element_info, hierarchy))
        
        # Estratégia 2: ClassName + Hierarquia
        if stability_analysis.get('class_name', {}).get('score', 0) >= 0.7:
            strategies.append(self._generate_class_hierarchy_strategy(element_info, hierarchy))
        
        # Estratégia 3: AutomationId (se parecer estável)
        if stability_analysis.get('automation_id', {}).get('score', 0) >= 0.6:
            strategies.append(self._generate_automation_id_strategy(element_info, hierarchy))
        
        # Estratégia 4: Posição relativa (âncora visual)
        strategies.append(self._generate_visual_anchor_strategy(element_info, hierarchy))
        
        # Estratégia 5: Índice entre irmãos
        strategies.append(self._generate_sibling_index_strategy(element_info, hierarchy))
        
        # Estratégia 6: Coordenadas relativas (fallback)
        strategies.append(self._generate_coordinate_fallback_strategy(element_info, hierarchy))
        
        # Remove estratégias inválidas
        valid_strategies = [s for s in strategies if s and s.get('xml_content')]
        
        return valid_strategies
    
    def _generate_name_hierarchy_strategy(self, element_info, hierarchy):
        """
        Gera estratégia baseada em Name + ControlType + Hierarquia
        
        Args:
            element_info: Informações do elemento
            hierarchy: Contexto hierárquico
            
        Returns:
            dict: Estratégia de seleção
        """
        if not element_info.get('name'):
            return None
        
        # Constrói caminho hierárquico usando nomes estáveis
        xml_parts = []
        
        # Adiciona janela (sempre importante para contexto)
        window = hierarchy[0] if hierarchy else {}
        if window.get('control_type') in ['WindowControl', 'Window']:
            title = window.get('name', '')
            class_name = window.get('class_name', '')
            if title:
                xml_parts.append(f'<Window title="{self._escape_xml(title)}" className="{self._escape_xml(class_name)}" />')
        
        # Adiciona containers intermediários importantes
        for level in hierarchy[1:-1]:  # Pula janela e elemento final
            if level.get('control_type') in ['PanelControl', 'GroupControl', 'TabControl', 'ToolBarControl']:
                if level.get('name'):
                    xml_parts.append(f'<Container name="{self._escape_xml(level["name"])}" controlType="{level["control_type"]}" />')
                elif level.get('automation_id'):
                    xml_parts.append(f'<Container automationId="{self._escape_xml(level["automation_id"])}" controlType="{level["control_type"]}" />')
        
        # Adiciona elemento target
        name = element_info.get('name', '')
        control_type = element_info.get('control_type', '')
        class_name = element_info.get('class_name', '')
        
        element_attrs = [f'name="{self._escape_xml(name)}"']
        if control_type:
            element_attrs.append(f'controlType="{control_type}"')
        if class_name:
            element_attrs.append(f'className="{self._escape_xml(class_name)}"')
        
        xml_parts.append(f'<Element {" ".join(element_attrs)} />')
        
        xml_content = f'<Selector>{"".join(xml_parts)}</Selector>'
        
        return {
            'name': 'name_hierarchy',
            'description': 'Estratégia baseada em Name + ControlType + Hierarquia',
            'reliability_score': 0.92,
            'xml_content': xml_content,
            'attributes_used': ['name', 'control_type', 'hierarchy'],
            'robustness': 'high'
        }
    
    def _generate_class_hierarchy_strategy(self, element_info, hierarchy):
        """
        Gera estratégia baseada em ClassName + Hierarquia
        
        Args:
            element_info: Informações do elemento
            hierarchy: Contexto hierárquico
            
        Returns:
            dict: Estratégia de seleção
        """
        if not element_info.get('class_name'):
            return None
        
        xml_parts = []
        
        # Adiciona janela
        window = hierarchy[0] if hierarchy else {}
        if window.get('control_type') in ['WindowControl', 'Window']:
            title = window.get('name', '')
            if title:
                xml_parts.append(f'<Window title="{self._escape_xml(title)}" />')
        
        # Adiciona elemento target com ClassName
        class_name = element_info.get('class_name', '')
        control_type = element_info.get('control_type', '')
        
        # Calcula índice entre elementos do mesmo tipo
        target_element = hierarchy[-1] if hierarchy else {}
        sibling_info = target_element.get('sibling_index', {})
        same_type_index = sibling_info.get('same_type_index', 0)
        
        element_attrs = [f'className="{self._escape_xml(class_name)}"']
        if control_type:
            element_attrs.append(f'controlType="{control_type}"')
        if same_type_index > 0:
            element_attrs.append(f'index="{same_type_index}"')
        
        xml_parts.append(f'<Element {" ".join(element_attrs)} />')
        
        xml_content = f'<Selector>{"".join(xml_parts)}</Selector>'
        
        return {
            'name': 'class_hierarchy',
            'description': 'Estratégia baseada em ClassName + Índice',
            'reliability_score': 0.82,
            'xml_content': xml_content,
            'attributes_used': ['class_name', 'control_type', 'index'],
            'robustness': 'medium-high'
        }
    
    def _generate_automation_id_strategy(self, element_info, hierarchy):
        """
        Gera estratégia baseada em AutomationId (apenas se confiável)
        
        Args:
            element_info: Informações do elemento
            hierarchy: Contexto hierárquico
            
        Returns:
            dict: Estratégia de seleção
        """
        automation_id = element_info.get('automation_id')
        if not automation_id:
            return None
        
        xml_parts = []
        
        # Adiciona janela para contexto
        window = hierarchy[0] if hierarchy else {}
        if window.get('control_type') in ['WindowControl', 'Window']:
            title = window.get('name', '')
            if title:
                xml_parts.append(f'<Window title="{self._escape_xml(title)}" />')
        
        # Adiciona elemento com AutomationId
        control_type = element_info.get('control_type', '')
        element_attrs = [f'automationId="{self._escape_xml(automation_id)}"']
        if control_type:
            element_attrs.append(f'controlType="{control_type}"')
        
        xml_parts.append(f'<Element {" ".join(element_attrs)} />')
        
        xml_content = f'<Selector>{"".join(xml_parts)}</Selector>'
        
        return {
            'name': 'automation_id',
            'description': 'Estratégia baseada em AutomationId estável',
            'reliability_score': 0.75,
            'xml_content': xml_content,
            'attributes_used': ['automation_id', 'control_type'],
            'robustness': 'medium'
        }
    
    def _generate_visual_anchor_strategy(self, element_info, hierarchy):
        """
        Gera estratégia baseada em âncora visual (elementos próximos)
        
        Args:
            element_info: Informações do elemento
            hierarchy: Contexto hierárquico
            
        Returns:
            dict: Estratégia de seleção
        """
        # Esta estratégia precisa de informações sobre elementos irmãos
        # Por simplicidade, vamos usar posição relativa baseada em índice
        
        xml_parts = []
        
        # Adiciona janela
        window = hierarchy[0] if hierarchy else {}
        if window.get('control_type') in ['WindowControl', 'Window']:
            title = window.get('name', '')
            if title:
                xml_parts.append(f'<Window title="{self._escape_xml(title)}" />')
        
        # Tenta encontrar elemento pai com nome para usar como âncora
        anchor_found = False
        for level in reversed(hierarchy[:-1]):  # Do elemento para janela
            if level.get('name') and level.get('control_type') in ['GroupControl', 'PanelControl', 'ToolBarControl']:
                xml_parts.append(f'<Anchor name="{self._escape_xml(level["name"])}" controlType="{level["control_type"]}" />')
                anchor_found = True
                break
        
        if not anchor_found:
            # Usa container genérico como âncora
            parent = hierarchy[-2] if len(hierarchy) > 1 else {}
            if parent.get('class_name'):
                xml_parts.append(f'<Container className="{self._escape_xml(parent["class_name"])}" />')
        
        # Adiciona elemento target com múltiplos atributos
        control_type = element_info.get('control_type', '')
        name = element_info.get('name', '')
        class_name = element_info.get('class_name', '')
        
        element_attrs = []
        if name:
            element_attrs.append(f'name="{self._escape_xml(name)}"')
        if control_type:
            element_attrs.append(f'controlType="{control_type}"')
        if class_name and not name:  # Só usa ClassName se não tiver Name
            element_attrs.append(f'className="{self._escape_xml(class_name)}"')
        
        if element_attrs:
            xml_parts.append(f'<Element {" ".join(element_attrs)} />')
        else:
            return None  # Não conseguiu criar estratégia válida
        
        xml_content = f'<Selector>{"".join(xml_parts)}</Selector>'
        
        return {
            'name': 'visual_anchor',
            'description': 'Estratégia baseada em âncora visual/contexto',
            'reliability_score': 0.78,
            'xml_content': xml_content,
            'attributes_used': ['anchor', 'name', 'control_type'],
            'robustness': 'medium'
        }
    
    def _generate_sibling_index_strategy(self, element_info, hierarchy):
        """
        Gera estratégia baseada em índice entre elementos irmãos
        
        Args:
            element_info: Informações do elemento
            hierarchy: Contexto hierárquico
            
        Returns:
            dict: Estratégia de seleção
        """
        xml_parts = []
        
        # Adiciona janela
        window = hierarchy[0] if hierarchy else {}
        if window.get('control_type') in ['WindowControl', 'Window']:
            title = window.get('name', '')
            if title:
                xml_parts.append(f'<Window title="{self._escape_xml(title)}" />')
        
        # Adiciona pai direto se disponível
        parent = hierarchy[-2] if len(hierarchy) > 1 else {}
        if parent.get('class_name'):
            xml_parts.append(f'<Container className="{self._escape_xml(parent["class_name"])}" />')
        
        # Adiciona elemento por ControlType + índice
        control_type = element_info.get('control_type', '')
        target_element = hierarchy[-1] if hierarchy else {}
        sibling_info = target_element.get('sibling_index', {})
        index = sibling_info.get('index', 0)
        
        element_attrs = []
        if control_type:
            element_attrs.append(f'controlType="{control_type}"')
        element_attrs.append(f'index="{index}"')
        
        xml_parts.append(f'<Element {" ".join(element_attrs)} />')
        
        xml_content = f'<Selector>{"".join(xml_parts)}</Selector>'
        
        return {
            'name': 'sibling_index',
            'description': 'Estratégia baseada em índice entre irmãos',
            'reliability_score': 0.65,
            'xml_content': xml_content,
            'attributes_used': ['control_type', 'index'],
            'robustness': 'medium-low'
        }
    
    def _generate_coordinate_fallback_strategy(self, element_info, hierarchy):
        """
        Gera estratégia de fallback baseada em coordenadas relativas
        
        Args:
            element_info: Informações do elemento
            hierarchy: Contexto hierárquico
            
        Returns:
            dict: Estratégia de seleção
        """
        xml_parts = []
        
        # Adiciona janela
        window = hierarchy[0] if hierarchy else {}
        if window.get('control_type') in ['WindowControl', 'Window']:
            title = window.get('name', '')
            if title:
                xml_parts.append(f'<Window title="{self._escape_xml(title)}" />')
        
        # Usa coordenadas relativas à janela
        target_element = hierarchy[-1] if hierarchy else {}
        bounding_rect = target_element.get('bounding_rect')
        
        if bounding_rect:
            # Calcula posição relativa (percentual da janela)
            window_rect = window.get('bounding_rect', {})
            if window_rect:
                rel_x = ((bounding_rect['left'] - window_rect.get('left', 0)) / window_rect.get('width', 1)) * 100
                rel_y = ((bounding_rect['top'] - window_rect.get('top', 0)) / window_rect.get('height', 1)) * 100
                
                xml_parts.append(f'<Element coordinateX="{rel_x:.1f}%" coordinateY="{rel_y:.1f}%" tolerance="5" />')
            else:
                # Coordenadas absolutas como último recurso
                center_x = bounding_rect['left'] + bounding_rect['width'] // 2
                center_y = bounding_rect['top'] + bounding_rect['height'] // 2
                xml_parts.append(f'<Element coordinateX="{center_x}" coordinateY="{center_y}" tolerance="10" />')
        else:
            return None  # Sem coordenadas disponíveis
        
        xml_content = f'<Selector>{"".join(xml_parts)}</Selector>'
        
        return {
            'name': 'coordinate_fallback',
            'description': 'Estratégia de fallback por coordenadas',
            'reliability_score': 0.45,
            'xml_content': xml_content,
            'attributes_used': ['coordinates'],
            'robustness': 'low'
        }
    
    def _escape_xml(self, text):
        """
        Escapa caracteres especiais para XML
        
        Args:
            text: Texto a ser escapado
            
        Returns:
            str: Texto escapado
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
    
    def _validate_and_rank_strategies(self, strategies, element):
        """
        Valida e ordena estratégias por confiabilidade real
        
        Args:
            strategies: Lista de estratégias geradas
            element: Elemento original para teste
            
        Returns:
            list: Estratégias validadas e ordenadas
        """
        validated_strategies = []
        
        print_info(f"Validando {len(strategies)} estratégias...")
        
        for i, strategy in enumerate(strategies):
            if not strategy:
                continue
                
            print_info(f"Testando estratégia {i+1}: {strategy['name']}")
            
            try:
                # Testa se o seletor consegue encontrar o elemento
                found_element = self.executor.execute_selector(strategy['xml_content'], timeout=2)
                
                if found_element:
                    # Verifica se é o elemento correto
                    if self._is_same_element(found_element, element):
                        strategy['validation_status'] = 'success'
                        strategy['validation_message'] = 'Elemento encontrado corretamente'
                        validated_strategies.append(strategy)
                        print_success(f"✓ Estratégia {strategy['name']} validada")
                    else:
                        strategy['validation_status'] = 'wrong_element'
                        strategy['validation_message'] = 'Seletor encontrou elemento diferente'
                        print_warning(f"⚠ Estratégia {strategy['name']} encontrou elemento errado")
                else:
                    strategy['validation_status'] = 'not_found'
                    strategy['validation_message'] = 'Elemento não encontrado'
                    print_warning(f"✗ Estratégia {strategy['name']} não encontrou elemento")
                    
            except Exception as e:
                strategy['validation_status'] = 'error'
                strategy['validation_message'] = f'Erro durante validação: {str(e)}'
                print_error(f"✗ Erro ao testar estratégia {strategy['name']}: {str(e)}")
        
        # Ordena por reliability_score (maior primeiro)
        validated_strategies.sort(key=lambda x: x.get('reliability_score', 0), reverse=True)
        
        print_success(f"✓ {len(validated_strategies)} estratégias validadas com sucesso")
        
        return validated_strategies
    
    def _is_same_element(self, element1, element2):
        """
        Verifica se dois elementos são o mesmo
        
        Args:
            element1: Primeiro elemento
            element2: Segundo elemento
            
        Returns:
            bool: True se são o mesmo elemento
        """
        try:
            # Compara RuntimeId (mais confiável)
            if hasattr(element1, 'RuntimeId') and hasattr(element2, 'RuntimeId'):
                runtime1 = getattr(element1, 'RuntimeId', None)
                runtime2 = getattr(element2, 'RuntimeId', None)
                if runtime1 and runtime2:
                    return list(runtime1) == list(runtime2)
            
            # Fallback: compara múltiplas propriedades
            props_to_compare = ['AutomationId', 'Name', 'ClassName', 'ControlTypeName']
            
            for prop in props_to_compare:
                val1 = getattr(element1, prop, '')
                val2 = getattr(element2, prop, '')
                if val1 != val2:
                    return False
            
            # Compara posição (BoundingRectangle)
            try:
                rect1 = element1.BoundingRectangle
                rect2 = element2.BoundingRectangle
                if rect1 and rect2:
                    # Permite diferença de até 2 pixels (para pequenas mudanças)
                    return (abs(rect1.left - rect2.left) <= 2 and 
                           abs(rect1.top - rect2.top) <= 2 and
                           abs(rect1.right - rect2.right) <= 2 and
                           abs(rect1.bottom - rect2.bottom) <= 2)
            except:
                pass
            
            return True  # Se chegou até aqui, provavelmente é o mesmo
            
        except Exception:
            return False
    
    def _calculate_overall_reliability(self, validated_strategies):
        """
        Calcula confiabilidade geral baseada nas estratégias validadas
        
        Args:
            validated_strategies: Lista de estratégias validadas
            
        Returns:
            float: Score de confiabilidade geral (0-100)
        """
        if not validated_strategies:
            return 0.0
        
        # Score baseado na melhor estratégia validada
        best_score = validated_strategies[0].get('reliability_score', 0) * 100
        
        # Bônus por ter múltiplas estratégias funcionando
        strategy_count_bonus = min(len(validated_strategies) * 5, 15)  # Máximo 15% de bônus
        
        # Bônus por diversidade de estratégias
        strategy_types = set(s.get('robustness', '') for s in validated_strategies)
        diversity_bonus = len(strategy_types) * 3  # 3% por tipo diferente
        
        total_score = best_score + strategy_count_bonus + diversity_bonus
        
        return min(total_score, 100.0)  # Máximo 100%
    
    def _build_final_xml_selector(self, validated_strategies):
        """
        Constrói seletor XML final com múltiplas estratégias
        
        Args:
            validated_strategies: Estratégias validadas
            
        Returns:
            str: XML final com estratégias ordenadas
        """
        if not validated_strategies:
            return '<Selector><Element error="Nenhuma estratégia válida" /></Selector>'
        
        # Usa a melhor estratégia como principal
        primary_strategy = validated_strategies[0]
        
        # Constrói XML com metadata e fallbacks
        xml_lines = [
            f'<!-- Seletor Ultra-Robusto gerado em {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} -->',
            f'<!-- Estratégia principal: {primary_strategy["name"]} (confiabilidade: {primary_strategy["reliability_score"]*100:.1f}%) -->',
            f'<!-- Estratégias de fallback: {len(validated_strategies)-1} disponíveis -->',
            '',
            primary_strategy['xml_content']
        ]
        
        # Adiciona estratégias de fallback como comentários informativos
        if len(validated_strategies) > 1:
            xml_lines.extend([
                '',
                '<!-- ESTRATÉGIAS DE FALLBACK (para implementação futura): -->'
            ])
            
            for i, strategy in enumerate(validated_strategies[1:], 2):
                xml_lines.extend([
                    f'<!-- Fallback {i}: {strategy["name"]} (confiabilidade: {strategy["reliability_score"]*100:.1f}%) -->',
                    f'<!-- {strategy["xml_content"]} -->'
                ])
        
        return '\n'.join(xml_lines)
    
    def get_stability_report(self, element_info, stability_analysis):
        """
        Gera relatório detalhado de estabilidade dos atributos
        
        Args:
            element_info: Informações do elemento
            stability_analysis: Análise de estabilidade
            
        Returns:
            dict: Relatório formatado
        """
        report = {
            'summary': {},
            'recommendations': [],
            'warnings': []
        }
        
        # Analisa cada atributo
        for attr_name, analysis in stability_analysis.items():
            score = analysis.get('score', 0)
            value = analysis.get('value', '')
            
            report['summary'][attr_name] = {
                'score': score,
                'classification': self._classify_stability_score(score),
                'value': value[:50] + '...' if len(str(value)) > 50 else str(value)
            }
            
            # Gera recomendações baseadas na análise
            if attr_name == 'automation_id' and score < 0.5:
                report['warnings'].append(f"AutomationId '{value}' parece dinâmico - evite usar como atributo principal")
            elif attr_name == 'name' and score > 0.8:
                report['recommendations'].append(f"Name '{value}' é muito estável - recomendado como atributo principal")
            elif attr_name == 'class_name' and score > 0.7:
                report['recommendations'].append(f"ClassName '{value}' é confiável para uso hierárquico")
        
        # Recomendação geral
        best_attributes = [attr for attr, analysis in stability_analysis.items() 
                          if analysis.get('score', 0) >= 0.7]
        
        if best_attributes:
            report['recommendations'].insert(0, f"Atributos mais estáveis encontrados: {', '.join(best_attributes)}")
        else:
            report['warnings'].insert(0, "Nenhum atributo altamente estável encontrado - seletor pode ser instável")
        
        return report
    
    def _classify_stability_score(self, score):
        """
        Classifica score de estabilidade em categoria textual
        
        Args:
            score: Score de estabilidade (0-1)
            
        Returns:
            str: Classificação textual
        """
        if score >= 0.9:
            return "EXCELENTE"
        elif score >= 0.7:
            return "BOA"
        elif score >= 0.5:
            return "MODERADA"
        elif score >= 0.3:
            return "BAIXA"
        else:
            return "PÉSSIMA"