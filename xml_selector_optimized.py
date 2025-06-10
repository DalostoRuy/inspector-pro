"""
Gerador de Seletores XML Otimizado para Windows Desktop
Versão 1.0 - Focado em estratégias que realmente funcionam

Este módulo é otimizado especificamente para aplicações Windows Desktop
(Delphi, WinForms, Win32) com base em análise real de falhas e sucessos.
"""
import re
import time
import json
from datetime import datetime
from xml_selector_generator import XMLSelectorGenerator
from xml_selector_executor import XMLSelectorExecutor
from utils import print_info, print_success, print_warning, print_error

class OptimizedSelectorGenerator:
    """
    Gerador otimizado que foca apenas em estratégias que funcionam
    
    Este gerador foi criado com base em análise real de falhas do sistema
    ultra-robusto e foca em estratégias simples e efetivas.
    """
    
    def __init__(self):
        """Inicializa o gerador otimizado"""
        self.base_generator = XMLSelectorGenerator()
        self.executor = XMLSelectorExecutor()
        
        # Estratégias ordenadas por efetividade real
        self.strategy_priority = [
            'name_control_type',      # Mais efetiva para botões/controles
            'automation_id_simple',   # AutomationId direto quando disponível
            'class_name_window',      # ClassName + contexto de janela
            'mixed_attributes',       # Combinação de atributos estáveis
            'hierarchy_simple'        # Hierarquia simplificada
        ]
        
    def generate_optimized_selector(self, element):
        """
        Gera seletor otimizado baseado em estratégias que realmente funcionam
        
        Args:
            element: Elemento UI Automation capturado
            
        Returns:
            dict: Seletor otimizado com múltiplas estratégias testadas
        """
        print_info("🎯 Gerando seletor XML OTIMIZADO...")
        
        start_time = time.time()
        
        try:
            # 1. Extrai informações do elemento
            element_info = self._extract_element_info(element)
            
            # 2. Analisa qual estratégia usar baseado no tipo de elemento
            best_strategy = self._determine_best_strategy(element_info)
            
            # 3. Gera seletores usando estratégias otimizadas
            generated_selectors = self._generate_working_selectors(element_info, element)
            
            # 4. Testa e valida apenas as estratégias geradas
            validated_selectors = self._test_selectors_real_time(generated_selectors, element)
            
            # 5. Constrói resultado otimizado
            result = {
                'optimized_selector': self._build_best_selector(validated_selectors),
                'working_selectors': validated_selectors,
                'recommended_strategy': best_strategy,
                'element_analysis': element_info,
                'generation_metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'generation_time': time.time() - start_time,
                    'reliability_score': self._calculate_reliability_score(validated_selectors),
                    'strategies_tested': len(generated_selectors),
                    'strategies_working': len(validated_selectors)
                }
            }
            
            working_count = len(validated_selectors)
            total_count = len(generated_selectors)
            reliability = result['generation_metadata']['reliability_score']
            
            print_success(f"✅ Seletor otimizado gerado: {working_count}/{total_count} estratégias funcionando")
            print_info(f"🏆 Confiabilidade: {reliability:.1f}% | Melhor estratégia: {best_strategy}")
            
            return result
            
        except Exception as e:
            print_error(f"Erro ao gerar seletor otimizado: {str(e)}")
            return None
            
    def _extract_element_info(self, element):
        """Extrai informações básicas e úteis do elemento"""
        try:
            # Obtém janela pai
            window_info = self._get_window_info(element)
            
            # Obtém informações do elemento
            element_data = {
                'automation_id': getattr(element, 'AutomationId', '') or '',
                'name': getattr(element, 'Name', '') or '',
                'class_name': getattr(element, 'ClassName', '') or '',
                'control_type': getattr(element, 'ControlTypeName', '') or '',
                'localized_control_type': getattr(element, 'LocalizedControlType', '') or '',
                'framework_id': getattr(element, 'FrameworkId', '') or '',
                'value': getattr(element, 'Value', '') or '',
                'is_enabled': getattr(element, 'IsEnabled', True),
                'window': window_info,
                'legacy_accessible_name': '',
                'legacy_accessible_description': '',
                'legacy_accessible_role_string': ''
            }

            # Extrair informações do LegacyIAccessiblePattern
            try:
                legacy_pattern = element.GetLegacyIAccessiblePattern()
                if legacy_pattern:
                    element_data['legacy_accessible_name'] = legacy_pattern.Name or ''
                    element_data['legacy_accessible_description'] = legacy_pattern.Description or ''
                    element_data['legacy_accessible_role_string'] = legacy_pattern.RoleString or ''
            except Exception as e:
                # Silenciosamente ignora se o padrão não for suportado ou ocorrer outro erro
                # print_warning(f"Não foi possível obter LegacyIAccessiblePattern: {str(e)}")
                pass

            # Calcula score de utilidade para cada atributo
            element_data['attribute_scores'] = self._score_attributes(element_data)
            
            return element_data
            
        except Exception as e:
            print_warning(f"Erro ao extrair informações: {str(e)}")
            return {}
    
    def _get_window_info(self, element):
        """Obtém informações da janela pai de forma eficiente"""
        try:
            current = element
            max_levels = 5  # Limitado para performance
            
            for _ in range(max_levels):
                if current.ControlTypeName == 'WindowControl':
                    return {
                        'title': current.Name or '',
                        'class_name': current.ClassName or '',
                        'automation_id': current.AutomationId or ''
                    }
                
                parent = current.GetParentControl()
                if not parent or parent == current:
                    break
                current = parent
            
            return {'title': '', 'class_name': '', 'automation_id': ''}
            
        except Exception:
            return {'title': '', 'class_name': '', 'automation_id': ''}
    
    def _score_attributes(self, element_data):
        """Calcula score de utilidade real para cada atributo"""
        scores = {}
        
        # Detecta se é aplicação Delphi
        is_delphi_app = self._is_delphi_application(element_data)
        
        # Name - muito bom para botões com texto fixo
        name = element_data.get('name', '')
        if name and not re.search(r'\d{4,}', name):  # Sem números longos
            scores['name'] = 0.9
        elif name:
            scores['name'] = 0.6
        else:
            scores['name'] = 0.0
            
        # ControlType - sempre útil
        control_type = element_data.get('control_type', '')
        scores['control_type'] = 1.0 if control_type else 0.0
        
        # ClassName - CRÍTICO para aplicações Delphi, especialmente quando Name vazio
        class_name = element_data.get('class_name', '')
        if class_name and class_name.startswith(('TDB', 'TEdit', 'TcxDB', 'TcxEdit')):
            # Campos Delphi específicos - score máximo quando Name vazio
            scores['class_name'] = 0.98 if not name else 0.95
        elif class_name and class_name.startswith(('T', 'Tcx', 'Button', 'Edit')):
            scores['class_name'] = 0.95 if is_delphi_app else 0.8
        elif class_name:
            scores['class_name'] = 0.8
        else:
            scores['class_name'] = 0.0
            
        # AutomationId - score ajustado baseado no contexto Delphi
        automation_id = element_data.get('automation_id', '')
        if automation_id and automation_id.isdigit():
            if is_delphi_app and not name:  # Campo Delphi sem Name
                scores['automation_id'] = 0.7  # Score melhor para campos Delphi
            elif len(automation_id) < 10:
                scores['automation_id'] = 0.6
            else:
                scores['automation_id'] = 0.4  # IDs muito longos são dinâmicos
        elif automation_id:
            scores['automation_id'] = 0.4
        else:
            scores['automation_id'] = 0.0
            
        # Window title - crucial para contexto Delphi
        window_title = element_data.get('window', {}).get('title', '')
        scores['window_title'] = 0.9 if window_title and is_delphi_app else 0.85 if window_title else 0.0

        # LegacyAccessibleName - pode ser muito útil se vier de um label
        legacy_name = element_data.get('legacy_accessible_name', '')
        if legacy_name and not legacy_name.isdigit() and len(legacy_name) > 2:
            scores['legacy_accessible_name'] = 0.9
        elif legacy_name:
            scores['legacy_accessible_name'] = 0.5 # Menos útil se for numérico ou curto
        else:
            scores['legacy_accessible_name'] = 0.0
        
        return scores
    
    def _is_delphi_application(self, element_data):
        """Detecta se é uma aplicação Delphi baseada em padrões"""
        # Verifica ClassName do elemento
        class_name = element_data.get('class_name', '')
        if class_name.startswith(('T', 'Tcx', 'TDB', 'TEdit')):
            return True
            
        # Verifica ClassName da janela
        window_class = element_data.get('window', {}).get('class_name', '')
        if window_class.startswith(('TForm', 'TFrm', 'T')):
            return True
            
        # Verifica título da janela por padrões Delphi
        window_title = element_data.get('window', {}).get('title', '')
        if any(keyword in window_title.lower() for keyword in ['delphi', 'borland', 'embarcadero']):
            return True
            
        return False
    
    def _determine_best_strategy(self, element_info):
        """Determina a melhor estratégia baseada no elemento"""
        scores = element_info.get('attribute_scores', {})
        name = element_info.get('name', '')
        is_delphi_app = self._is_delphi_application(element_info)
        
        # PRIORIDADE 1: ClassName para campos Delphi sem Name (TDBEdit, TEdit, etc.)
        if (not name and scores.get('class_name', 0) >= 0.9 and 
            scores.get('control_type', 0) >= 0.9 and is_delphi_app):
            return 'class_name_window'
        
        # PRIORIDADE 2: Name+ControlType quando Name é bom
        if scores.get('name', 0) >= 0.8 and scores.get('control_type', 0) >= 0.9:
            return 'name_control_type'
        
        # PRIORIDADE 3: ClassName geral para aplicações Delphi
        if scores.get('class_name', 0) >= 0.9 and scores.get('control_type', 0) >= 0.9:
            return 'class_name_window'
        
        # PRIORIDADE 4: AutomationId quando disponível com Window
        if scores.get('automation_id', 0) >= 0.6 and scores.get('window_title', 0) >= 0.8:
            return 'automation_id_simple'
            
        # Estratégia mista para casos complexos
        return 'mixed_attributes'
    
    def _generate_working_selectors(self, element_info, element):
        """Gera apenas seletores que têm alta chance de funcionar"""
        selectors = []

        # PRIORIDADES ATUALIZADAS:
        # 0: Label Anchored (via AccessibleName) - Nova, muito alta prioridade se aplicável
        # 1: Stable Parent + Typed Index - Nova, alta prioridade
        # 2: Name + ControlType (originalmente 1)
        # 3: ClassName + Window (originalmente 1 ou 2/3) - Especialmente para Delphi
        # 4: AutomationId simples (originalmente 2)
        # 5: Delphi Field Context (originalmente 2)
        # 6: Mixed Attributes (originalmente 4)
        # 7: Traditional Fallback (originalmente 5)

        # Nova Estratégia: Label Anchored (via AccessibleName)
        label_anchored_result = self._create_label_anchored_selector(element_info, element)
        if label_anchored_result:
            selectors.append({
                'name': 'label_anchored_accessible_name',
                'xml': label_anchored_result['xml'],
                'priority': 0, # Altíssima prioridade
                'description': label_anchored_result['description']
            })

        # Nova Estratégia: Stable Parent + Typed Index
        stable_parent_typed_index_result = self._create_stable_parent_typed_index_selector(element_info, element)
        if stable_parent_typed_index_result:
            selectors.append({
                'name': 'stable_parent_typed_index',
                'xml': stable_parent_typed_index_result['xml'],
                'priority': 1, # Alta prioridade
                'description': stable_parent_typed_index_result['description']
            })
        
        # Estratégia: Name + ControlType
        if element_info['attribute_scores'].get('name', 0) >= 0.5:
            selector_name_ctrl = self._create_name_control_selector(element_info)
            if selector_name_ctrl:
                selectors.append({
                    'name': 'name_control_type',
                    'xml': selector_name_ctrl,
                    'priority': 2, # Prioridade ajustada
                    'description': 'Name + ControlType'
                })
        
        # Estratégia: ClassName + Window
        if element_info['attribute_scores'].get('class_name', 0) >= 0.8:
            selector_class_win = self._create_class_window_selector(element_info)
            if selector_class_win:
                is_delphi_field = (element_info.get('class_name', '').startswith(('TDB', 'TEdit', 'Tcx')) and 
                                 not element_info.get('name', ''))
                # Delphi fields sem nome ainda são muito importantes com ClassName
                priority = 2 if is_delphi_field else 3 # Prioridade ajustada
                selectors.append({
                    'name': 'class_name_window',
                    'xml': selector_class_win,
                    'priority': priority,
                    'description': 'ClassName + Window (Delphi otimizado)' if is_delphi_field else 'ClassName + Window'
                })
        
        # Estratégia: AutomationId simples
        if element_info['attribute_scores'].get('automation_id', 0) >= 0.6:
            selector_auto_id = self._create_automation_id_selector(element_info)
            if selector_auto_id:
                selectors.append({
                    'name': 'automation_id_simple',
                    'xml': selector_auto_id,
                    'priority': 4, # Prioridade ajustada
                    'description': 'AutomationId direto'
                })
        
        # Estratégia: Contexto específico Delphi
        if (element_info.get('class_name', '').startswith(('TDB', 'TEdit', 'Tcx')) and 
            not element_info.get('name', '')): # Focado em campos Delphi sem nome explícito
            selector_delphi_ctx = self._create_delphi_context_selector(element_info, element)
            if selector_delphi_ctx:
                selectors.append({
                    'name': 'delphi_field_context',
                    'xml': selector_delphi_ctx,
                    'priority': 5,  # Prioridade ajustada
                    'description': 'Contexto Delphi com Parent'
                })
        
        # Estratégia: Atributos mistos
        selector_mixed = self._create_mixed_attributes_selector(element_info)
        if selector_mixed:
            selectors.append({
                'name': 'mixed_attributes',
                'xml': selector_mixed,
                'priority': 6, # Prioridade ajustada
                'description': 'Múltiplos atributos'
            })
        
        # Estratégia: Fallback com gerador tradicional
        try:
            traditional_selectors = self.base_generator.generate_robust_selector(element)
            if traditional_selectors and len(traditional_selectors) > 0:
                selectors.append({
                    'name': 'traditional_fallback',
                    'xml': traditional_selectors[0],
                    'priority': 5,
                    'description': 'Gerador tradicional'
                })
        except Exception:
            pass
        
        print_info(f"📝 Geradas {len(selectors)} estratégias otimizadas")
        return selectors

    def _create_label_anchored_selector(self, element_info, element):
        """
        Tenta criar um seletor baseado no LegacyIAccessiblePattern.Name,
        que frequentemente corresponde ao texto de um label associado.
        """
        legacy_name = element_info.get('legacy_accessible_name', '')
        class_name = element_info.get('class_name', '')
        control_type = element_info.get('control_type', '')
        window_title = element_info.get('window', {}).get('title', '')

        # Verifica se o legacy_accessible_name é útil
        if not legacy_name or legacy_name.isdigit() or len(legacy_name) < 3 or len(legacy_name) > 100:
            return None

        legacy_name_escaped = self._escape_xml(legacy_name)
        class_name_escaped = self._escape_xml(class_name)

        xml_parts = []

        if window_title:
            window_escaped = self._escape_xml(window_title)
            xml_parts.append(f'<Window title="{window_escaped}" />')

        element_attrs = []
        if class_name_escaped: # Adiciona className se disponível e útil
            element_attrs.append(f'className="{class_name_escaped}"')
        if control_type:
            element_attrs.append(f'controlType="{control_type}"')

        element_attrs.append(f'accessibleName="{legacy_name_escaped}"') # Novo atributo conceitual

        xml_parts.append(f'<Element {" ".join(element_attrs)} />')

        return {
            'xml': f'<Selector>{"".join(xml_parts)}</Selector>',
            'description': 'Label via AccessibleName'
        }

    def _create_stable_parent_typed_index_selector(self, element_info, element):
        """
        Tenta criar um seletor encontrando um pai estável e usando um índice
        baseado no tipo (ClassName e ControlType) do elemento.
        """
        window_title = element_info.get('window', {}).get('title', '')
        element_class_name = element_info.get('class_name', '')
        element_control_type = element_info.get('control_type', '')

        if not element_class_name or not element_control_type: # Precisa do tipo do elemento
            return None

        current = element
        stable_parent_info = None
        parent_element = None

        # Navega para cima para encontrar um pai estável (max 3-4 níveis)
        for _ in range(4):
            try:
                parent = current.GetParentControl()
                if not parent or parent == current:
                    break

                parent_name = getattr(parent, 'Name', '') or ''
                parent_automation_id = getattr(parent, 'AutomationId', '') or ''
                parent_class_name = getattr(parent, 'ClassName', '') or ''
                parent_control_type = getattr(parent, 'ControlTypeName', '') or ''

                # Critérios de estabilidade do pai
                is_stable = False
                parent_attrs_list = []

                if parent_name and not parent_name.isdigit() and len(parent_name) > 2:
                    is_stable = True
                    parent_attrs_list.append(f'name="{self._escape_xml(parent_name)}"')
                elif parent_automation_id and not parent_automation_id.isdigit():
                    is_stable = True
                    parent_attrs_list.append(f'automationId="{self._escape_xml(parent_automation_id)}"')
                elif parent_class_name and not parent_class_name.startswith(('T', 'WindowsForms10')) and \
                     parent_class_name not in ['Pane', 'Custom'] : # Evitar classes genéricas demais
                    is_stable = True
                    parent_attrs_list.append(f'className="{self._escape_xml(parent_class_name)}"')

                if parent_control_type : # ControlType é sempre bom ter
                     parent_attrs_list.append(f'controlType="{self._escape_xml(parent_control_type)}"')


                if is_stable and parent_attrs_list:
                    stable_parent_info = " ".join(parent_attrs_list)
                    parent_element = parent
                    break

                current = parent
            except Exception: # Problemas ao acessar GetParentControl ou atributos
                break

        if not stable_parent_info or not parent_element:
            return None

        # Encontra o índice do elemento entre os filhos do mesmo tipo do pai estável
        typed_index = -1
        try:
            children = parent_element.GetChildren()
            filtered_children = []
            for child in children:
                child_class_name = getattr(child, 'ClassName', '') or ''
                child_control_type = getattr(child, 'ControlTypeName', '') or ''
                if child_class_name == element_class_name and child_control_type == element_control_type:
                    filtered_children.append(child)

            for i, child in enumerate(filtered_children):
                # Compara AutomationId ou Name para identificar o elemento original
                # Esta é uma simplificação; uma comparação mais robusta pode ser necessária
                if (getattr(child, 'AutomationId', '') == element_info.get('automation_id') and
                    getattr(child, 'Name', '') == element_info.get('name')):
                    typed_index = i
                    break
            # Fallback se não encontrar por ID/Name (p. ex. elementos sem ID/Name únicos)
            if typed_index == -1 and element in filtered_children:
                 # This might be risky if elements are identical beyond name/automationId
                 # A more robust way would be to compare the element objects directly if possible
                 # For now, we assume the 'element' object is comparable or its position is what we get
                 # from GetChildren() list.
                 # Let's try to find by object reference (requires element to be in children)
                try:
                    typed_index = [c.AutomationId for c in filtered_children].index(element.AutomationId) # Simplistic
                except ValueError: # Element not found by AutomationId, try by object ref if possible
                    # This direct object comparison might not work across different wrappers/proxies
                    # but it's worth a try if AutomationId is not unique or available
                    for i, child_ref in enumerate(filtered_children):
                        if child_ref == element: # This relies on object identity
                            typed_index = i
                            break


        except Exception: # Erro ao obter filhos ou seus atributos
            return None

        if typed_index == -1:
            return None

        xml_parts = []
        if window_title:
            window_escaped = self._escape_xml(window_title)
            xml_parts.append(f'<Window title="{window_escaped}" />')

        # Estrutura aninhada: Pai Estável > Elemento com typedIndex
        xml_parts.append(f'<Element {stable_parent_info}>')
        xml_parts.append(f'<Element className="{self._escape_xml(element_class_name)}" controlType="{self._escape_xml(element_control_type)}" typedIndex="{typed_index}" />')
        xml_parts.append('</Element>') # Fechamento do pai

        return {
            'xml': f'<Selector>{"".join(xml_parts)}</Selector>',
            'description': 'Stable Parent + Typed Index'
        }

    def _create_name_control_selector(self, element_info):
        """Cria seletor baseado em Name + ControlType"""
        name = element_info.get('name', '')
        control_type = element_info.get('control_type', '')
        window_title = element_info.get('window', {}).get('title', '')
        
        if not name or not control_type:
            return None
        
        # Escapa caracteres especiais do XML
        name_escaped = self._escape_xml(name)
        
        xml_parts = []
        
        # Adiciona contexto da janela se disponível
        if window_title:
            window_escaped = self._escape_xml(window_title)
            xml_parts.append(f'<Window title="{window_escaped}" />')
        
        # Elemento principal
        xml_parts.append(f'<Element name="{name_escaped}" controlType="{control_type}" />')
        
        return f'<Selector>{"".join(xml_parts)}</Selector>'
    
    def _create_automation_id_selector(self, element_info):
        """Cria seletor baseado em AutomationId"""
        automation_id = element_info.get('automation_id', '')
        control_type = element_info.get('control_type', '')
        window_title = element_info.get('window', {}).get('title', '')
        
        if not automation_id:
            return None
        
        xml_parts = []
        
        # Contexto da janela
        if window_title:
            window_escaped = self._escape_xml(window_title)
            xml_parts.append(f'<Window title="{window_escaped}" />')
        
        # Elemento com AutomationId
        element_attrs = [f'automationId="{automation_id}"']
        if control_type:
            element_attrs.append(f'controlType="{control_type}"')
        
        xml_parts.append(f'<Element {" ".join(element_attrs)} />')
        
        return f'<Selector>{"".join(xml_parts)}</Selector>'
    
    def _create_class_window_selector(self, element_info):
        """Cria seletor baseado em ClassName + Window"""
        class_name = element_info.get('class_name', '')
        control_type = element_info.get('control_type', '')
        window_title = element_info.get('window', {}).get('title', '')
        
        if not class_name:
            return None
        
        xml_parts = []
        
        # Janela como contexto
        if window_title:
            window_escaped = self._escape_xml(window_title)
            xml_parts.append(f'<Window title="{window_escaped}" />')
        
        # Elemento com ClassName
        element_attrs = [f'className="{class_name}"']
        if control_type:
            element_attrs.append(f'controlType="{control_type}"')
        
        xml_parts.append(f'<Element {" ".join(element_attrs)} />')
        
        return f'<Selector>{"".join(xml_parts)}</Selector>'
    
    def _create_delphi_context_selector(self, element_info, element):
        """Cria seletor específico para campos Delphi usando contexto completo"""
        try:
            class_name = element_info.get('class_name', '')
            control_type = element_info.get('control_type', '')
            window_title = element_info.get('window', {}).get('title', '')
            
            if not class_name or not window_title:
                return None
            
            xml_parts = []
            
            # Contexto da janela
            window_escaped = self._escape_xml(window_title)
            xml_parts.append(f'<Window title="{window_escaped}" />')
            
            # Tenta obter informações do parent
            try:
                parent = element.GetParentControl()
                if parent and hasattr(parent, 'ClassName'):
                    parent_class = getattr(parent, 'ClassName', '')
                    parent_name = getattr(parent, 'Name', '')
                    
                    # Se parent é um container Delphi (TGroupBox, TPanel)
                    if parent_class.startswith(('TGroup', 'TPanel')):
                        parent_attrs = [f'className="{parent_class}"']
                        if parent_name:
                            parent_name_escaped = self._escape_xml(parent_name)
                            parent_attrs.append(f'name="{parent_name_escaped}"')
                        
                        xml_parts.append(f'<Element {" ".join(parent_attrs)} />')
            except Exception:
                pass  # Se não conseguir obter parent, continua sem ele
            
            # Elemento principal
            element_attrs = [f'className="{class_name}"']
            if control_type:
                element_attrs.append(f'controlType="{control_type}"')
            
            xml_parts.append(f'<Element {" ".join(element_attrs)} />')
            
            return f'<Selector>{"".join(xml_parts)}</Selector>'
            
        except Exception:
            return None
    
    def _create_mixed_attributes_selector(self, element_info):
        """Cria seletor com múltiplos atributos para robustez"""
        scores = element_info.get('attribute_scores', {})
        
        # Seleciona os melhores atributos disponíveis
        best_attributes = []
        
        if scores.get('name', 0) >= 0.6:
            name_escaped = self._escape_xml(element_info.get('name', ''))
            best_attributes.append(f'name="{name_escaped}"')
        
        if scores.get('class_name', 0) >= 0.7:
            class_name_escaped = self._escape_xml(element_info.get('class_name', ''))
            best_attributes.append(f'className="{class_name_escaped}"')
        
        if scores.get('control_type', 0) >= 0.9:
            best_attributes.append(f'controlType="{element_info.get("control_type", "")}"')
        
        if not best_attributes:
            return None
        
        # Constrói seletor
        xml_parts = []
        
        window_title = element_info.get('window', {}).get('title', '')
        if window_title:
            window_escaped = self._escape_xml(window_title)
            xml_parts.append(f'<Window title="{window_escaped}" />')
        
        xml_parts.append(f'<Element {" ".join(best_attributes)} />')
        
        return f'<Selector>{"".join(xml_parts)}</Selector>'
    
    def _test_selectors_real_time(self, selectors, original_element):
        """Testa seletores em tempo real e retorna apenas os que funcionam"""
        working_selectors = []
        
        print_info(f"🧪 Testando {len(selectors)} seletores em tempo real...")
        
        for i, selector_info in enumerate(selectors):
            xml_selector = selector_info['xml']
            strategy_name = selector_info['name']
            
            print_info(f"Testando estratégia {i+1}: {strategy_name}")
            
            try:
                # Tenta executar o seletor
                start_time = time.time()
                found_element = self.executor.execute_selector(xml_selector, timeout=3)
                execution_time = time.time() - start_time
                
                if found_element:
                    # Verifica se encontrou o elemento correto
                    if self._verify_element_match(found_element, original_element):
                        selector_info['execution_time'] = execution_time
                        selector_info['validation_status'] = 'working'
                        selector_info['validation_message'] = 'Elemento encontrado e verificado'
                        working_selectors.append(selector_info)
                        print_success(f"✅ Estratégia {strategy_name} FUNCIONANDO ({execution_time:.2f}s)")
                    else:
                        print_warning(f"⚠️ Estratégia {strategy_name} encontrou elemento diferente")
                else:
                    print_warning(f"❌ Estratégia {strategy_name} não encontrou elemento")
                    
            except Exception as e:
                print_warning(f"❌ Erro na estratégia {strategy_name}: {str(e)}")
        
        print_success(f"🎯 {len(working_selectors)} estratégias funcionando de {len(selectors)} testadas")
        return working_selectors
    
    def _verify_element_match(self, found_element, original_element):
        """Verifica se o elemento encontrado é o mesmo que o original"""
        try:
            # Compara atributos principais
            props_to_check = ['AutomationId', 'Name', 'ClassName', 'ControlTypeName']
            
            for prop in props_to_check:
                original_val = getattr(original_element, prop, '') or ''
                found_val = getattr(found_element, prop, '') or ''
                
                # Se algum atributo importante não bate, não é o mesmo
                if original_val and found_val and original_val != found_val:
                    return False
            
            # Se passou nos testes básicos, considera como sendo o mesmo
            return True
            
        except Exception:
            return False
    
    def _build_best_selector(self, working_selectors):
        """Constrói o melhor seletor baseado nos que funcionam"""
        if not working_selectors:
            return '<Selector><Element error="Nenhum seletor funcionando" /></Selector>'
        
        # Ordena por prioridade (menor = melhor)
        working_selectors.sort(key=lambda x: x.get('priority', 999))
        
        best_selector = working_selectors[0]
        
        # Adiciona comentários informativos
        xml_lines = [
            f'<!-- Seletor Otimizado - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} -->',
            f'<!-- Estratégia: {best_selector["description"]} -->',
            f'<!-- Tempo de execução: {best_selector.get("execution_time", 0):.2f}s -->',
            f'<!-- Alternativas disponíveis: {len(working_selectors)-1} -->',
            '',
            best_selector['xml']
        ]
        
        return '\n'.join(xml_lines)
    
    def _calculate_reliability_score(self, working_selectors):
        """Calcula score de confiabilidade baseado em estratégias funcionando"""
        if not working_selectors:
            return 0.0
        
        # Score base pela estratégia primária
        primary_strategy = working_selectors[0]['name']
        base_scores = {
            'name_control_type': 95,  # Maior prioridade para estratégia mais estável
            'class_name_window': 90,  # Aumentado - muito estável para Delphi
            'automation_id_simple': 70,  # Reduzido porque pode mudar
            'mixed_attributes': 80,
            'traditional_fallback': 60
        }
        
        base_score = base_scores.get(primary_strategy, 50)
        
        # Bônus por ter múltiplas estratégias funcionando
        strategy_bonus = min((len(working_selectors) - 1) * 5, 15)
        
        total_score = base_score + strategy_bonus
        return min(total_score, 100.0)
    
    def _escape_xml(self, text):
        """Escapa caracteres especiais para XML"""
        if not isinstance(text, str):
            text = str(text)
        
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&apos;')
        
        return text
    
    def get_optimization_report(self, element_info, working_selectors):
        """Gera relatório de otimização"""
        report = {
            'element_analysis': {
                'best_attributes': [],
                'problematic_attributes': [],
                'recommendations': []
            },
            'strategy_analysis': {
                'working_strategies': len(working_selectors),
                'best_strategy': working_selectors[0]['name'] if working_selectors else 'none',
                'execution_times': []
            },
            'optimization_suggestions': []
        }
        
        # Analisa atributos
        scores = element_info.get('attribute_scores', {})
        for attr, score in scores.items():
            if score >= 0.8:
                report['element_analysis']['best_attributes'].append(f"{attr} ({score:.1f})")
            elif score <= 0.3:
                report['element_analysis']['problematic_attributes'].append(f"{attr} ({score:.1f})")
        
        # Analisa estratégias
        for selector in working_selectors:
            exec_time = selector.get('execution_time', 0)
            report['strategy_analysis']['execution_times'].append({
                'strategy': selector['name'],
                'time': exec_time
            })
        
        # Gera recomendações
        if len(working_selectors) >= 2:
            report['optimization_suggestions'].append("Múltiplas estratégias funcionando - seletor muito robusto")
        elif len(working_selectors) == 1:
            report['optimization_suggestions'].append("Uma estratégia funcionando - considere backup manual")
        else:
            report['optimization_suggestions'].append("Nenhuma estratégia funcionando - elemento pode ser instável")
        
        return report

# Função de conveniência para usar o gerador otimizado
def generate_optimized_selector(element):
    """
    Função conveniente para gerar seletor otimizado
    
    Args:
        element: Elemento UI Automation
        
    Returns:
        dict: Resultado da geração otimizada
    """
    generator = OptimizedSelectorGenerator()
    return generator.generate_optimized_selector(element)