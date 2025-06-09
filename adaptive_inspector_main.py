"""
Adaptive Inspector Main Integration
Version 1.0 - Drop-in replacement for main.py with adaptive capabilities

This module provides a seamless upgrade path by replacing the main application
with adaptive-enhanced versions while maintaining full backward compatibility.
"""

import os
import sys
import time
from typing import Dict, List, Optional, Any

# Import adaptive components
from adaptive_integration_layer import (
    AdaptiveElementInspector, AdaptiveXMLSelectorExecutor, AdaptiveIntegrationLayer
)
from dynamic_selector_cache_schema import CacheConfiguration
from utils import *

class AdaptiveUIInspectorApp:
    """
    Enhanced version of UIInspectorApp with adaptive capabilities
    
    This class provides a drop-in replacement for the original application
    with full adaptive selector evolution features.
    """
    
    def __init__(self):
        """Initialize the adaptive UI inspector application"""
        self.adaptive_mode_enabled = True
        self.inspector = AdaptiveElementInspector(enable_adaptive_features=self.adaptive_mode_enabled)
        self.executor = AdaptiveXMLSelectorExecutor(enable_adaptive_features=self.adaptive_mode_enabled)
        
        # Configuration
        self.auto_healing_enabled = True
        self.adaptive_generation_enabled = True
        self.pattern_learning_enabled = True
        
        print_header("INSPECTOR PRO v3.0 - ADAPTIVE EDITION")
        print_colored("🚀 Sistema de Seletores Adaptativos Ativado", Fore.GREEN)
        print_colored("🧠 Inteligência Artificial Integrada", Fore.CYAN)
        print_colored("🔧 Auto-Reparação de Seletores Disponível", Fore.YELLOW)
        print()
    
    def run(self):
        """Execute main application loop with adaptive features"""
        while True:
            try:
                self._display_adaptive_main_menu()
                choice = input("\nEscolha uma opção: ").strip()
                
                if choice == '1':
                    self._adaptive_capture_element()
                elif choice == '2':
                    self._list_captured_elements()
                elif choice == '3':
                    self._adaptive_test_selector()
                elif choice == '4':
                    self._adaptive_execute_action()
                elif choice == '5':
                    self._show_adaptive_statistics()
                elif choice == '6':
                    self._adaptive_configuration_menu()
                elif choice == '7':
                    self._adaptive_healing_menu()
                elif choice == '8':
                    self._pattern_analysis_menu()
                elif choice == '0' or choice.lower() == 'q':
                    self._safe_exit()
                    break
                else:
                    print_warning("Opção inválida! Tente novamente.")
                
            except KeyboardInterrupt:
                print_warning("\nOperação interrompida pelo usuário")
            except Exception as e:
                print_error(f"Erro inesperado: {str(e)}")
                
            input("\nPressione Enter para continuar...")
    
    def _display_adaptive_main_menu(self):
        """Display enhanced main menu with adaptive features"""
        print_header("INSPECTOR PRO v3.0 - MENU PRINCIPAL ADAPTATIVO")
        
        # Show adaptive status
        if self.adaptive_mode_enabled:
            print_colored("🟢 Modo Adaptativo: ATIVO", Fore.GREEN)
            print_colored(f"🔧 Auto-Reparação: {'ATIVA' if self.auto_healing_enabled else 'INATIVA'}", 
                         Fore.GREEN if self.auto_healing_enabled else Fore.YELLOW)
            print_colored(f"🧠 Aprendizado de Padrões: {'ATIVO' if self.pattern_learning_enabled else 'INATIVO'}", 
                         Fore.GREEN if self.pattern_learning_enabled else Fore.YELLOW)
        else:
            print_colored("🟡 Modo Adaptativo: INATIVO (Compatibilidade)", Fore.YELLOW)
        
        print()
        print_colored("CAPTURA E GERAÇÃO:", Fore.CYAN)
        print_colored("  1. 🎯 Capturar Elemento (com IA)", Fore.WHITE)
        print()
        print_colored("TESTES E EXECUÇÃO:", Fore.CYAN)
        print_colored("  2. 📋 Listar Elementos Capturados", Fore.WHITE)
        print_colored("  3. 🧪 Testar Seletor XML (com validação adaptativa)", Fore.WHITE)
        print_colored("  4. ⚡ Executar Ação (com auto-reparação)", Fore.WHITE)
        print()
        print_colored("INTELIGÊNCIA ARTIFICIAL:", Fore.MAGENTA)
        print_colored("  5. 📊 Estatísticas do Sistema Adaptativo", Fore.WHITE)
        print_colored("  6. ⚙️  Configurações Adaptativas", Fore.WHITE)
        print_colored("  7. 🔧 Menu de Reparação de Seletores", Fore.WHITE)
        print_colored("  8. 🧠 Análise de Padrões AutomationId", Fore.WHITE)
        print()
        print_colored("  0. ❌ Sair", Fore.RED)
    
    def _adaptive_capture_element(self):
        """Enhanced element capture with adaptive features"""
        print_header("CAPTURA ADAPTATIVA DE ELEMENTO")
        
        element_name = input("Nome do elemento: ").strip()
        if not element_name:
            print_warning("Nome do elemento é obrigatório!")
            return
        
        print()
        print_colored("TIPOS DE CAPTURA:", Fore.CYAN)
        print_colored("  1. 🎯 Elemento único (com IA)", Fore.WHITE)
        print_colored("  2. ⚓ Elemento âncora + clique relativo", Fore.WHITE)
        
        capture_type_choice = input("\nTipo de captura (1-2): ").strip()
        
        capture_type = "element"
        if capture_type_choice == "2":
            capture_type = "anchor_relative"
        
        print_info("🚀 Iniciando captura com recursos adaptativos...")
        
        # Use adaptive capture
        result = self.inspector.start_capture_mode(element_name, capture_type)
        
        if result:
            print_success("✅ Captura realizada com sucesso!")
            
            # Show adaptive enhancements if available
            element_data = result.get('element_data', {})
            if element_data.get('adaptive_enhanced'):
                self._display_adaptive_capture_summary(element_data)
            
            # Offer additional adaptive features
            self._offer_post_capture_features(result, element_name)
        else:
            print_error("❌ Captura falhou")
    
    def _display_adaptive_capture_summary(self, element_data: Dict[str, Any]):
        """Display summary of adaptive enhancements"""
        print()
        print_header("MELHORIAS ADAPTATIVAS APLICADAS")
        
        # Adaptive selectors
        adaptive_selectors = element_data.get('adaptive_selectors', [])
        if adaptive_selectors:
            print_colored(f"🎯 {len(adaptive_selectors)} seletores adaptativos gerados", Fore.GREEN)
            
            best_selector = adaptive_selectors[0]
            print_colored(f"   Melhor estratégia: {best_selector.get('adaptive_strategy', 'N/A')}", Fore.CYAN)
            print_colored(f"   Confiabilidade prevista: {best_selector.get('reliability_prediction', 0):.1%}", Fore.CYAN)
            print_colored(f"   Performance prevista: {best_selector.get('performance_prediction', 0):.1%}", Fore.CYAN)
        
        # Pattern analysis
        pattern_analysis = element_data.get('pattern_analysis', {})
        if pattern_analysis.get('pattern_detected'):
            print_colored(f"🧠 Padrão AutomationId detectado: {pattern_analysis.get('pattern_type', 'desconhecido')}", Fore.MAGENTA)
            print_colored(f"   Confiança no padrão: {pattern_analysis.get('confidence', 0):.1%}", Fore.CYAN)
            if pattern_analysis.get('predictive_capability'):
                print_colored("   🔮 Capacidade preditiva disponível", Fore.GREEN)
        
        # Relationship context
        relationship_context = element_data.get('relationship_context', {})
        if relationship_context:
            anchors = relationship_context.get('stable_anchors', [])
            if anchors:
                print_colored(f"🗺️ {len(anchors)} âncoras de navegação identificadas", Fore.BLUE)
        
        # Cache information
        cache_id = element_data.get('adaptive_cache_id')
        if cache_id:
            print_colored(f"💾 Elemento armazenado para reparação automática: {cache_id[:8]}...", Fore.YELLOW)
    
    def _offer_post_capture_features(self, capture_result: Dict[str, Any], element_name: str):
        """Offer additional adaptive features after capture"""
        print()
        print_colored("RECURSOS ADAPTATIVOS DISPONÍVEIS:", Fore.CYAN)
        print_colored("  1. 🔍 Análise detalhada de padrões", Fore.WHITE)
        print_colored("  2. 🗺️ Mapeamento de relacionamentos", Fore.WHITE)
        print_colored("  3. 🧪 Teste de confiabilidade adaptativa", Fore.WHITE)
        print_colored("  4. ⏭️ Continuar para menu principal", Fore.WHITE)
        
        choice = input("\nEscolha um recurso (1-4): ").strip()
        
        if choice == "1":
            self._analyze_element_patterns(capture_result, element_name)
        elif choice == "2":
            self._create_relationship_mapping(capture_result, element_name)
        elif choice == "3":
            self._test_adaptive_reliability(capture_result, element_name)
    
    def _adaptive_test_selector(self):
        """Enhanced XML selector testing with adaptive features"""
        print_header("TESTE ADAPTATIVO DE SELETOR XML")
        
        xml_selector = input("Cole o seletor XML para testar: ").strip()
        if not xml_selector:
            print_warning("Seletor XML é obrigatório!")
            return
        
        print_info("🧪 Testando seletor com validação adaptativa...")
        
        # Use adaptive testing
        result = self.inspector.test_xml_selector(xml_selector)
        
        if result.get('success'):
            print_success("✅ Seletor válido!")
            
            # Show additional adaptive information
            reliability = result.get('reliability', {})
            if reliability:
                reliability_pct = reliability.get('reliability_percentage', 0)
                print_colored(f"🎯 Confiabilidade: {reliability_pct:.1f}%", Fore.GREEN)
        else:
            print_error("❌ Seletor inválido")
            
            # Offer adaptive healing if available
            if result.get('adaptive_healing_available'):
                print()
                print_colored("🔧 REPARAÇÃO ADAPTATIVA DISPONÍVEL", Fore.YELLOW)
                choice = input("Tentar reparar automaticamente? (s/n): ").strip().lower()
                
                if choice == 's':
                    self._attempt_selector_healing(xml_selector)
    
    def _adaptive_execute_action(self):
        """Enhanced action execution with adaptive capabilities"""
        print_header("EXECUÇÃO ADAPTATIVA DE AÇÃO")
        
        xml_selector = input("Cole o seletor XML: ").strip()
        if not xml_selector:
            print_warning("Seletor XML é obrigatório!")
            return
        
        print()
        print_colored("TIPOS DE AÇÃO:", Fore.CYAN)
        print_colored("  1. 🖱️ Clique simples", Fore.WHITE)
        print_colored("  2. 🖱️🖱️ Clique duplo", Fore.WHITE)
        print_colored("  3. 🖱️➡️ Clique direito", Fore.WHITE)
        
        action_choice = input("\nTipo de ação (1-3): ").strip()
        
        action_types = {"1": "click", "2": "double_click", "3": "right_click"}
        action_type = action_types.get(action_choice, "click")
        
        print()
        print_colored("CONFIGURAÇÕES ADAPTATIVAS:", Fore.CYAN)
        print_colored(f"  Auto-reparação: {'ATIVA' if self.auto_healing_enabled else 'INATIVA'}", 
                     Fore.GREEN if self.auto_healing_enabled else Fore.YELLOW)
        
        if not self.auto_healing_enabled:
            choice = input("Ativar auto-reparação para esta execução? (s/n): ").strip().lower()
            enable_healing = choice == 's'
        else:
            enable_healing = True
        
        print_info(f"⚡ Executando {action_type} com recursos adaptativos...")
        
        # Use adaptive execution
        result = self.executor.execute_click_action(xml_selector, action_type, timeout=10)
        
        self._display_execution_result(result, action_type)
    
    def _display_execution_result(self, result: Dict[str, Any], action_type: str):
        """Display detailed execution result with adaptive information"""
        if result.get('success'):
            print_success(f"✅ {action_type.title()} executado com sucesso!")
            
            # Show execution path
            execution_path = result.get('execution_path', 'unknown')
            if execution_path == 'standard':
                print_colored("📍 Caminho: Execução padrão", Fore.GREEN)
            elif execution_path == 'healed_success':
                print_colored("📍 Caminho: Reparação adaptativa bem-sucedida", Fore.MAGENTA)
                print_colored(f"🔧 Estratégia de reparação: {result.get('healing_strategy', 'N/A')}", Fore.CYAN)
                print_colored(f"🎯 Confiança na reparação: {result.get('healing_confidence', 0):.1%}", Fore.CYAN)
                
                if result.get('new_automation_id'):
                    print_colored(f"🆔 Novo AutomationId descoberto: {result['new_automation_id']}", Fore.YELLOW)
            
            # Show timing
            total_time = result.get('total_execution_time', result.get('execution_time', 0))
            print_colored(f"⏱️ Tempo total: {total_time:.2f}s", Fore.CYAN)
            
        else:
            print_error(f"❌ {action_type.title()} falhou")
            
            # Show failure details
            execution_path = result.get('execution_path', 'unknown')
            if execution_path == 'standard_failed':
                print_colored("📍 Falha na execução padrão", Fore.RED)
                if result.get('healing_available'):
                    print_colored("💡 Sugestão: Auto-reparação está disponível", Fore.YELLOW)
            elif execution_path == 'healing_failed':
                print_colored("📍 Execução padrão e reparação adaptativa falharam", Fore.RED)
                healing_result = result.get('healing_result', {})
                if healing_result.get('error_message'):
                    print_colored(f"🔧 Erro na reparação: {healing_result['error_message']}", Fore.YELLOW)
            
            # Show error message
            error_msg = result.get('error_message', result.get('error', 'Erro desconhecido'))
            print_colored(f"❌ Erro: {error_msg}", Fore.RED)
    
    def _show_adaptive_statistics(self):
        """Show comprehensive adaptive system statistics"""
        print_header("ESTATÍSTICAS DO SISTEMA ADAPTATIVO")
        
        if not self.adaptive_mode_enabled:
            print_warning("Recursos adaptativos estão desativados")
            return
        
        try:
            stats = self.inspector.get_adaptive_statistics()
            
            # Integration layer stats
            integration_stats = stats.get('integration_layer', {})
            print_colored("CAMADA DE INTEGRAÇÃO:", Fore.CYAN)
            print_colored(f"  Capturas adaptativas: {integration_stats.get('adaptive_captures', 0)}", Fore.WHITE)
            print_colored(f"  Tentativas de reparação: {integration_stats.get('healing_attempts', 0)}", Fore.WHITE)
            print_colored(f"  Reparações bem-sucedidas: {integration_stats.get('successful_healings', 0)}", Fore.WHITE)
            print_colored(f"  Taxa de sucesso da reparação: {integration_stats.get('healing_success_rate', 0):.1f}%", Fore.GREEN)
            
            # System health
            system_health = stats.get('system_health', {})
            if system_health:
                print()
                print_colored("SAÚDE DO SISTEMA:", Fore.MAGENTA)
                print_colored(f"  Tamanho do cache: {system_health.get('cache_size', 0)} entradas", Fore.WHITE)
                print_colored(f"  Taxa de acerto do cache: {system_health.get('cache_hit_rate', 0):.1f}%", Fore.WHITE)
                print_colored(f"  Taxa geral de reparação: {system_health.get('overall_healing_success', 0):.1f}%", Fore.WHITE)
                print_colored(f"  Taxa de detecção de padrões: {system_health.get('pattern_detection_rate', 0):.1f}%", Fore.WHITE)
            
            # Component statistics
            component_stats = stats.get('component_statistics', {})
            if component_stats:
                print()
                print_colored("ESTATÍSTICAS DOS COMPONENTES:", Fore.YELLOW)
                
                # Show key metrics from each component
                for component, comp_stats in component_stats.items():
                    if isinstance(comp_stats, dict) and comp_stats:
                        print_colored(f"  {component.replace('_', ' ').title()}:", Fore.CYAN)
                        
                        # Show the most relevant metrics
                        if 'total_discoveries' in comp_stats:
                            success_rate = comp_stats.get('overall_success_rate', 0)
                            print_colored(f"    Descobertas: {comp_stats['total_discoveries']} (sucesso: {success_rate:.1f}%)", Fore.WHITE)
                        
                        if 'total_analyses' in comp_stats:
                            pattern_rate = comp_stats.get('pattern_success_rate', 0)
                            print_colored(f"    Análises: {comp_stats['total_analyses']} (padrões: {pattern_rate:.1f}%)", Fore.WHITE)
                        
                        if 'total_healing_requests' in comp_stats:
                            healing_rate = comp_stats.get('overall_success_rate', 0)
                            print_colored(f"    Reparações: {comp_stats['total_healing_requests']} (sucesso: {healing_rate:.1f}%)", Fore.WHITE)
            
        except Exception as e:
            print_error(f"Erro ao obter estatísticas: {str(e)}")
    
    def _adaptive_configuration_menu(self):
        """Configuration menu for adaptive features"""
        while True:
            print_header("CONFIGURAÇÕES ADAPTATIVAS")
            
            print_colored("ESTADO ATUAL:", Fore.CYAN)
            print_colored(f"  Modo Adaptativo: {'ATIVO' if self.adaptive_mode_enabled else 'INATIVO'}", 
                         Fore.GREEN if self.adaptive_mode_enabled else Fore.RED)
            print_colored(f"  Auto-Reparação: {'ATIVA' if self.auto_healing_enabled else 'INATIVA'}", 
                         Fore.GREEN if self.auto_healing_enabled else Fore.RED)
            print_colored(f"  Geração Adaptativa: {'ATIVA' if self.adaptive_generation_enabled else 'INATIVA'}", 
                         Fore.GREEN if self.adaptive_generation_enabled else Fore.RED)
            print_colored(f"  Aprendizado de Padrões: {'ATIVO' if self.pattern_learning_enabled else 'INATIVO'}", 
                         Fore.GREEN if self.pattern_learning_enabled else Fore.RED)
            
            print()
            print_colored("OPÇÕES:", Fore.CYAN)
            print_colored("  1. 🔄 Alternar Modo Adaptativo", Fore.WHITE)
            print_colored("  2. 🔧 Alternar Auto-Reparação", Fore.WHITE)
            print_colored("  3. 🎯 Alternar Geração Adaptativa", Fore.WHITE)
            print_colored("  4. 🧠 Alternar Aprendizado de Padrões", Fore.WHITE)
            print_colored("  5. 💾 Salvar Dados Adaptativos", Fore.WHITE)
            print_colored("  6. 🗑️ Limpar Cache Adaptativo", Fore.WHITE)
            print_colored("  0. ⬅️ Voltar ao Menu Principal", Fore.WHITE)
            
            choice = input("\nEscolha uma opção: ").strip()
            
            if choice == '1':
                self._toggle_adaptive_mode()
            elif choice == '2':
                self.auto_healing_enabled = not self.auto_healing_enabled
                status = "ATIVADA" if self.auto_healing_enabled else "DESATIVADA"
                print_success(f"Auto-reparação {status}")
            elif choice == '3':
                self.adaptive_generation_enabled = not self.adaptive_generation_enabled
                status = "ATIVADA" if self.adaptive_generation_enabled else "DESATIVADA"
                print_success(f"Geração adaptativa {status}")
            elif choice == '4':
                self.pattern_learning_enabled = not self.pattern_learning_enabled
                status = "ATIVO" if self.pattern_learning_enabled else "INATIVO"
                print_success(f"Aprendizado de padrões {status}")
            elif choice == '5':
                self._save_adaptive_data()
            elif choice == '6':
                self._clear_adaptive_cache()
            elif choice == '0':
                break
            else:
                print_warning("Opção inválida!")
            
            if choice != '0':
                input("\nPressione Enter para continuar...")
    
    def _toggle_adaptive_mode(self):
        """Toggle adaptive mode on/off"""
        if self.adaptive_mode_enabled:
            self.adaptive_mode_enabled = False
            self.inspector.adaptive_layer.disable_adaptive_mode()
            self.executor.adaptive_layer.disable_adaptive_mode()
            print_warning("Modo adaptativo DESATIVADO - modo de compatibilidade ativo")
        else:
            self.adaptive_mode_enabled = True
            self.inspector.adaptive_layer.enable_adaptive_mode()
            self.executor.adaptive_layer.enable_adaptive_mode()
            print_success("Modo adaptativo ATIVADO - recursos de IA disponíveis")
    
    def _save_adaptive_data(self):
        """Save adaptive data to disk"""
        if not self.adaptive_mode_enabled:
            print_warning("Modo adaptativo está desativado")
            return
        
        print_info("💾 Salvando dados adaptativos...")
        
        try:
            success = self.inspector.adaptive_layer.save_adaptive_data()
            if success:
                print_success("✅ Dados adaptativos salvos com sucesso")
            else:
                print_error("❌ Falha ao salvar dados adaptativos")
        except Exception as e:
            print_error(f"Erro ao salvar: {str(e)}")
    
    def _clear_adaptive_cache(self):
        """Clear adaptive cache"""
        if not self.adaptive_mode_enabled:
            print_warning("Modo adaptativo está desativado")
            return
        
        print_warning("⚠️ Esta ação irá limpar todo o cache adaptativo")
        choice = input("Tem certeza? (s/n): ").strip().lower()
        
        if choice == 's':
            try:
                self.inspector.adaptive_layer.cache.clear_cache()
                print_success("✅ Cache adaptativo limpo")
            except Exception as e:
                print_error(f"Erro ao limpar cache: {str(e)}")
    
    def _adaptive_healing_menu(self):
        """Menu for selector healing operations"""
        print_header("MENU DE REPARAÇÃO ADAPTATIVA")
        
        if not self.adaptive_mode_enabled:
            print_warning("Modo adaptativo está desativado")
            return
        
        xml_selector = input("Cole o seletor XML para reparar: ").strip()
        if not xml_selector:
            print_warning("Seletor XML é obrigatório!")
            return
        
        self._attempt_selector_healing(xml_selector)
    
    def _attempt_selector_healing(self, xml_selector: str):
        """Attempt to heal a broken selector"""
        print_info("🔧 Iniciando reparação adaptativa...")
        
        try:
            # Use the enhanced executor's healing capability
            result = self.executor.adaptive_layer.enhance_xml_selector_execution(
                xml_selector, "find", enable_auto_healing=True
            )
            
            if result.get('success'):
                if result.get('healing_attempted') and result.get('healing_successful'):
                    print_success("🎉 Reparação bem-sucedida!")
                    print_colored(f"🔧 Estratégia: {result.get('healing_strategy', 'N/A')}", Fore.CYAN)
                    print_colored(f"🎯 Confiança: {result.get('healing_confidence', 0):.1%}", Fore.CYAN)
                    
                    healed_selector = result.get('healed_selector')
                    if healed_selector:
                        print()
                        print_colored("SELETOR REPARADO:", Fore.MAGENTA)
                        print_colored(healed_selector, Fore.WHITE)
                        
                        # Offer to save the healed selector
                        choice = input("\nSalvar seletor reparado? (s/n): ").strip().lower()
                        if choice == 's':
                            self._save_healed_selector(healed_selector, result)
                else:
                    print_success("✅ Seletor já estava funcionando")
            else:
                print_error("❌ Reparação falhou")
                error_msg = result.get('error_message', 'Erro desconhecido')
                print_colored(f"Erro: {error_msg}", Fore.RED)
                
        except Exception as e:
            print_error(f"Erro durante reparação: {str(e)}")
    
    def _save_healed_selector(self, healed_selector: str, healing_result: Dict[str, Any]):
        """Save a healed selector to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"healed_selector_{timestamp}.xml"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(healed_selector)
                f.write(f"\n\n<!-- Healing Information -->\n")
                f.write(f"<!-- Strategy: {healing_result.get('healing_strategy', 'N/A')} -->\n")
                f.write(f"<!-- Confidence: {healing_result.get('healing_confidence', 0):.1%} -->\n")
                f.write(f"<!-- Healed at: {datetime.now().isoformat()} -->\n")
            
            print_success(f"💾 Seletor reparado salvo em: {filename}")
            
        except Exception as e:
            print_error(f"Erro ao salvar: {str(e)}")
    
    def _pattern_analysis_menu(self):
        """Menu for AutomationId pattern analysis"""
        print_header("ANÁLISE DE PADRÕES AUTOMATIONID")
        
        if not self.adaptive_mode_enabled:
            print_warning("Modo adaptativo está desativado")
            return
        
        automation_id = input("Digite o AutomationId para análise: ").strip()
        if not automation_id:
            print_warning("AutomationId é obrigatório!")
            return
        
        print_info("🧠 Analisando padrões...")
        
        # Use the pattern analysis from adaptive layer
        pattern_analysis = self.inspector.adaptive_layer._analyze_automation_id_patterns(automation_id)
        
        print()
        print_colored("RESULTADO DA ANÁLISE:", Fore.CYAN)
        print_colored(f"AutomationId: {automation_id}", Fore.WHITE)
        print_colored(f"Padrão detectado: {'SIM' if pattern_analysis.get('pattern_detected') else 'NÃO'}", 
                     Fore.GREEN if pattern_analysis.get('pattern_detected') else Fore.RED)
        
        if pattern_analysis.get('pattern_detected'):
            print_colored(f"Tipo de padrão: {pattern_analysis.get('pattern_type', 'desconhecido')}", Fore.CYAN)
            print_colored(f"Confiança: {pattern_analysis.get('confidence', 0):.1%}", Fore.CYAN)
            print_colored(f"Capacidade preditiva: {'SIM' if pattern_analysis.get('predictive_capability') else 'NÃO'}", 
                         Fore.GREEN if pattern_analysis.get('predictive_capability') else Fore.YELLOW)
        
        print_colored(f"Análise realizada em: {pattern_analysis.get('analysis_timestamp', 'N/A')}", Fore.WHITE)
    
    def _list_captured_elements(self):
        """List captured elements (reuse original functionality)"""
        from main import list_captured_elements
        list_captured_elements()
    
    def _analyze_element_patterns(self, capture_result: Dict[str, Any], element_name: str):
        """Perform detailed pattern analysis on captured element"""
        print_header("ANÁLISE DETALHADA DE PADRÕES")
        print_info("🧠 Analisando padrões avançados...")
        
        element_data = capture_result.get('element_data', {})
        automation_id = element_data.get('automation_id')
        
        if automation_id:
            pattern_analysis = self.inspector.adaptive_layer._analyze_automation_id_patterns(automation_id)
            
            print_colored("ANÁLISE DE AUTOMATIONID:", Fore.CYAN)
            for key, value in pattern_analysis.items():
                if key != 'analysis_timestamp':
                    print_colored(f"  {key}: {value}", Fore.WHITE)
        else:
            print_warning("Elemento não possui AutomationId para análise")
    
    def _create_relationship_mapping(self, capture_result: Dict[str, Any], element_name: str):
        """Create detailed relationship mapping"""
        print_header("MAPEAMENTO DE RELACIONAMENTOS")
        print_info("🗺️ Criando mapeamento de relacionamentos...")
        
        element_data = capture_result.get('element_data', {})
        relationship_context = element_data.get('relationship_context', {})
        
        if relationship_context:
            print_colored("CONTEXTO DE RELACIONAMENTOS:", Fore.CYAN)
            
            stable_anchors = relationship_context.get('stable_anchors', [])
            if stable_anchors:
                print_colored(f"Âncoras estáveis encontradas: {len(stable_anchors)}", Fore.GREEN)
                for i, anchor in enumerate(stable_anchors, 1):
                    print_colored(f"  {i}. {anchor.get('type', 'N/A')}: {anchor.get('name', anchor.get('title', 'N/A'))}", Fore.WHITE)
            
            navigation_hints = relationship_context.get('navigation_hints', [])
            if navigation_hints:
                print_colored("Dicas de navegação:", Fore.YELLOW)
                for hint in navigation_hints:
                    print_colored(f"  • {hint}", Fore.WHITE)
        else:
            print_warning("Nenhum contexto de relacionamento encontrado")
    
    def _test_adaptive_reliability(self, capture_result: Dict[str, Any], element_name: str):
        """Test adaptive reliability of captured selectors"""
        print_header("TESTE DE CONFIABILIDADE ADAPTATIVA")
        print_info("🧪 Testando confiabilidade dos seletores...")
        
        element_data = capture_result.get('element_data', {})
        adaptive_selectors = element_data.get('adaptive_selectors', [])
        
        if adaptive_selectors:
            print_colored("TESTANDO SELETORES ADAPTATIVOS:", Fore.CYAN)
            
            for i, selector in enumerate(adaptive_selectors, 1):
                xml_selector = selector.get('xml_selector', '')
                if xml_selector:
                    print_colored(f"\nSeletor {i}:", Fore.YELLOW)
                    print_colored(f"  Estratégia: {selector.get('adaptive_strategy', 'N/A')}", Fore.WHITE)
                    print_colored(f"  Confiabilidade prevista: {selector.get('reliability_prediction', 0):.1%}", Fore.WHITE)
                    
                    # Test the selector
                    test_result = self.inspector.test_xml_selector(xml_selector)
                    if test_result.get('success'):
                        print_colored("  ✅ Teste: PASSOU", Fore.GREEN)
                    else:
                        print_colored("  ❌ Teste: FALHOU", Fore.RED)
        else:
            print_warning("Nenhum seletor adaptativo disponível para teste")
    
    def _safe_exit(self):
        """Safe exit with adaptive data saving"""
        print_info("🔄 Finalizando aplicação...")
        
        if self.adaptive_mode_enabled:
            print_info("💾 Salvando dados adaptativos...")
            try:
                self.inspector.adaptive_layer.save_adaptive_data()
                print_success("✅ Dados adaptativos salvos")
            except Exception as e:
                print_warning(f"Aviso ao salvar dados: {str(e)}")
        
        print_success("👋 Inspector Pro v3.0 Adaptive Edition finalizado")

def main():
    """Main entry point for adaptive application"""
    # Check if running on Windows
    if not sys.platform.startswith('win'):
        print_error("❌ Este aplicativo requer Windows (UIA - UI Automation)")
        print_info("O sistema de automação UI é específico do Windows")
        sys.exit(1)
    
    try:
        # Initialize and run adaptive application
        app = AdaptiveUIInspectorApp()
        app.run()
        
    except KeyboardInterrupt:
        print_warning("\n👋 Aplicação finalizada pelo usuário")
    except Exception as e:
        print_error(f"❌ Erro crítico: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()