"""
Teste das correções para campos TDBEdit (Delphi)
Script para validar se as modificações resolveram o problema de detecção
"""
import json
import time
from pathlib import Path
from xml_selector_optimized import OptimizedSelectorGenerator
from xml_selector_executor import XMLSelectorExecutor
from utils import print_info, print_success, print_error, print_warning

class MockElement:
    """Mock do elemento UI para simular o elemento TDBEdit capturado"""
    
    def __init__(self, element_data):
        self.AutomationId = element_data.get('automation_id', '')
        self.Name = element_data.get('name', '')
        self.ClassName = element_data.get('class_name', '')
        self.ControlTypeName = element_data.get('control_type', '')
        self.LocalizedControlType = element_data.get('localized_control_type', '')
        self.FrameworkId = element_data.get('framework_id', '')
        self.Value = element_data.get('value', '')
        self.IsEnabled = element_data.get('is_enabled', True)
        
        # Mock parent para simular hierarquia
        self._parent_info = element_data.get('parent_info', {})
        self._window_info = element_data.get('window_info', {})
    
    def GetParentControl(self):
        """Simula parent control baseado nos dados capturados"""
        if self._parent_info:
            parent = MockElement({
                'automation_id': self._parent_info.get('automation_id', ''),
                'name': self._parent_info.get('name', ''),
                'class_name': self._parent_info.get('class_name', ''),
                'control_type': self._parent_info.get('control_type', ''),
            })
            return parent
        return None

def test_tdb_edit_elements():
    """Testa as correções com elementos TDBEdit reais capturados"""
    print_info("🧪 Iniciando teste das correções para campos TDBEdit...")
    
    # Caminhos dos elementos capturados
    captured_dirs = [
        "captured_elements/tttt_20250609_211248",
        "captured_elements/daaaa_20250609_210457"
    ]
    
    generator = OptimizedSelectorGenerator()
    results = []
    
    for captured_dir in captured_dirs:
        element_file = Path(captured_dir) / "element_data.json"
        
        if not element_file.exists():
            print_warning(f"Arquivo não encontrado: {element_file}")
            continue
            
        print_info(f"\n📂 Testando elemento de: {captured_dir}")
        
        # Carrega dados do elemento
        with open(element_file, 'r', encoding='utf-8') as f:
            element_data = json.load(f)
        
        # Cria mock do elemento
        mock_element = MockElement(element_data)
        
        # Testa geração otimizada
        print_info("🎯 Gerando seletor otimizado...")
        start_time = time.time()
        
        try:
            result = generator.generate_optimized_selector(mock_element)
            generation_time = time.time() - start_time
            
            if result:
                working_selectors = result.get('working_selectors', [])
                reliability_score = result.get('generation_metadata', {}).get('reliability_score', 0)
                best_strategy = result.get('recommended_strategy', 'none')
                
                print_success(f"✅ Seletor gerado com sucesso!")
                print_info(f"🏆 Estratégias funcionando: {len(working_selectors)}")
                print_info(f"📊 Confiabilidade: {reliability_score:.1f}%")
                print_info(f"🎯 Melhor estratégia: {best_strategy}")
                
                # Analisa estratégias geradas
                print_info("\n📋 Estratégias disponíveis:")
                for i, selector in enumerate(working_selectors):
                    strategy_name = selector.get('name', 'unknown')
                    description = selector.get('description', 'N/A')
                    priority = selector.get('priority', 999)
                    print_info(f"  {i+1}. {strategy_name} (P{priority}) - {description}")
                
                results.append({
                    'element_file': str(element_file),
                    'success': True,
                    'reliability_score': reliability_score,
                    'strategies_count': len(working_selectors),
                    'best_strategy': best_strategy,
                    'generation_time': generation_time
                })
                
            else:
                print_error(f"❌ Falha na geração do seletor")
                results.append({
                    'element_file': str(element_file),
                    'success': False,
                    'error': 'Geração falhou'
                })
                
        except Exception as e:
            print_error(f"💥 Erro durante teste: {str(e)}")
            results.append({
                'element_file': str(element_file),
                'success': False,
                'error': str(e)
            })
    
    # Relatório final
    print_info("\n" + "="*60)
    print_info("📊 RELATÓRIO FINAL DOS TESTES")
    print_info("="*60)
    
    successful_tests = [r for r in results if r['success']]
    failed_tests = [r for r in results if not r['success']]
    
    print_success(f"✅ Testes bem-sucedidos: {len(successful_tests)}/{len(results)}")
    if failed_tests:
        print_error(f"❌ Testes falharam: {len(failed_tests)}")
    
    if successful_tests:
        avg_reliability = sum(r['reliability_score'] for r in successful_tests) / len(successful_tests)
        avg_strategies = sum(r['strategies_count'] for r in successful_tests) / len(successful_tests)
        avg_time = sum(r['generation_time'] for r in successful_tests) / len(successful_tests)
        
        print_info(f"📈 Confiabilidade média: {avg_reliability:.1f}%")
        print_info(f"🎯 Estratégias médias: {avg_strategies:.1f}")
        print_info(f"⏱️ Tempo médio: {avg_time:.2f}s")
        
        # Análise das estratégias mais utilizadas
        strategies_used = [r['best_strategy'] for r in successful_tests]
        strategy_counts = {}
        for strategy in strategies_used:
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        
        print_info("\n🏆 Estratégias mais utilizadas:")
        for strategy, count in sorted(strategy_counts.items(), key=lambda x: x[1], reverse=True):
            print_info(f"  - {strategy}: {count} vez(es)")
    
    return results

def test_specific_scenario():
    """Testa cenário específico: TDBEdit sem Name"""
    print_info("\n🎯 Teste específico: Campo TDBEdit sem Name")
    
    # Simula dados de um TDBEdit típico
    test_data = {
        'automation_id': '853206',
        'name': '',  # VAZIO - problema original
        'class_name': 'TDBEdit',
        'control_type': 'EditControl',
        'localized_control_type': 'editar',
        'framework_id': 'Win32',
        'value': '09/06/2025',
        'is_enabled': True,
        'parent_info': {
            'automation_id': '460994',
            'name': 'Informações principais da matéria',
            'class_name': 'TGroupBox',
            'control_type': 'PaneControl'
        },
        'window_info': {
            'title': 'Matérias - Edição\\inclusão',
            'class_name': 'TFrmMateriasEdit'
        }
    }
    
    # Cria elemento mock
    mock_element = MockElement(test_data)
    
    # Testa extração de informações
    generator = OptimizedSelectorGenerator()
    element_info = generator._extract_element_info(mock_element)
    
    print_info("📊 Análise do elemento:")
    print_info(f"  - Name: '{element_info.get('name', '')}'")
    print_info(f"  - ClassName: '{element_info.get('class_name', '')}'")
    print_info(f"  - ControlType: '{element_info.get('control_type', '')}'")
    
    # Testa scoring
    scores = element_info.get('attribute_scores', {})
    print_info("\n🎯 Scores dos atributos:")
    for attr, score in scores.items():
        print_info(f"  - {attr}: {score:.2f}")
    
    # Testa detecção Delphi
    is_delphi = generator._is_delphi_application(element_info)
    print_info(f"\n🔍 Aplicação Delphi detectada: {'SIM' if is_delphi else 'NÃO'}")
    
    # Testa determinação de estratégia
    best_strategy = generator._determine_best_strategy(element_info)
    print_info(f"🎯 Melhor estratégia determinada: {best_strategy}")
    
    return {
        'is_delphi_detected': is_delphi,
        'best_strategy': best_strategy,
        'scores': scores,
        'name_empty': not element_info.get('name', ''),
        'classname_score': scores.get('class_name', 0)
    }

if __name__ == "__main__":
    print_info("🚀 Iniciando testes das correções para TDBEdit")
    
    # Teste 1: Cenário específico
    specific_result = test_specific_scenario()
    
    # Teste 2: Elementos reais capturados
    real_results = test_tdb_edit_elements()
    
    # Validação final
    print_info("\n" + "="*60)
    print_info("🎉 VALIDAÇÃO DAS CORREÇÕES")
    print_info("="*60)
    
    # Verifica se as correções estão funcionando
    corrections_working = True
    issues = []
    
    # Verifica detecção Delphi
    if not specific_result['is_delphi_detected']:
        corrections_working = False
        issues.append("❌ Detecção de aplicação Delphi não está funcionando")
    else:
        print_success("✅ Detecção de aplicação Delphi funcionando")
    
    # Verifica priorização de estratégia
    expected_strategies = ['class_name_window', 'delphi_field_context']
    if specific_result['best_strategy'] not in expected_strategies:
        corrections_working = False
        issues.append(f"❌ Estratégia {specific_result['best_strategy']} não é a esperada para campos Delphi")
    else:
        print_success(f"✅ Estratégia correta selecionada: {specific_result['best_strategy']}")
    
    # Verifica scoring de ClassName
    if specific_result['classname_score'] < 0.9:
        corrections_working = False
        issues.append(f"❌ Score de ClassName muito baixo: {specific_result['classname_score']}")
    else:
        print_success(f"✅ Score de ClassName adequado: {specific_result['classname_score']:.2f}")
    
    # Verifica resultados dos testes reais
    successful_real_tests = [r for r in real_results if r.get('success', False)]
    if len(successful_real_tests) == 0:
        corrections_working = False
        issues.append("❌ Nenhum teste com elementos reais foi bem-sucedido")
    else:
        avg_reliability = sum(r['reliability_score'] for r in successful_real_tests) / len(successful_real_tests)
        if avg_reliability < 80:
            corrections_working = False
            issues.append(f"❌ Confiabilidade média muito baixa: {avg_reliability:.1f}%")
        else:
            print_success(f"✅ Confiabilidade adequada nos testes reais: {avg_reliability:.1f}%")
    
    # Resultado final
    if corrections_working:
        print_success("\n🎉 CORREÇÕES IMPLEMENTADAS COM SUCESSO!")
        print_success("Os campos TDBEdit agora devem ser detectados corretamente.")
    else:
        print_error("\n❌ CORREÇÕES PRECISAM DE AJUSTES:")
        for issue in issues:
            print_error(f"  {issue}")