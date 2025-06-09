"""
Validador de Seletores XML
Versão 1.0 - Combina geração e validação de seletores executáveis

Este módulo integra XMLSelectorGenerator e XMLSelectorExecutor para criar
um sistema completo de geração e validação de seletores XML funcionais.
"""
import time
from xml_selector_generator import XMLSelectorGenerator
from xml_selector_executor import XMLSelectorExecutor
from utils import print_info, print_success, print_warning, print_error

class XMLSelectorValidator:
    """
    Classe que combina geração e validação de seletores XML
    
    Esta classe gera múltiplos seletores para um elemento e os valida
    automaticamente, retornando apenas seletores que realmente funcionam.
    """
    
    def __init__(self):
        """
        Inicializa o validador com gerador e executor
        """
        self.generator = XMLSelectorGenerator()
        self.executor = XMLSelectorExecutor()
        self.validation_timeout = 3  # Timeout reduzido para validação rápida
        
    def generate_and_validate_selectors(self, element, validate_immediately=True):
        """
        Gera seletores executáveis e os valida automaticamente
        
        Args:
            element: Elemento UI Automation capturado
            validate_immediately: Se True, valida seletores imediatamente
            
        Returns:
            dict: Resultado com seletores válidos e relatório
        """
        result = {
            'valid_selectors': [],
            'invalid_selectors': [],
            'validation_reports': [],
            'generation_time': 0,
            'validation_time': 0,
            'total_time': 0
        }
        
        start_time = time.time()
        
        try:
            # Gera seletores executáveis
            print_info("Gerando seletores XML executáveis...")
            generation_start = time.time()
            
            selectors = self.generator.generate_executable_selectors(element)
            
            result['generation_time'] = time.time() - generation_start
            print_success(f"Gerados {len(selectors)} seletores em {result['generation_time']:.3f}s")
            
            if not validate_immediately:
                # Se não validar imediatamente, retorna todos como válidos
                result['valid_selectors'] = selectors
                result['total_time'] = time.time() - start_time
                return result
            
            # Valida cada seletor
            print_info("Validando seletores...")
            validation_start = time.time()
            
            # Extrai informações esperadas do elemento original
            expected_info = self._extract_expected_info(element)
            
            for i, selector in enumerate(selectors):
                print_info(f"Validando seletor {i+1}/{len(selectors)}...")
                
                validation_result = self.executor.validate_selector(
                    selector, 
                    expected_info, 
                    timeout=self.validation_timeout
                )
                
                validation_result['selector_index'] = i
                validation_result['selector'] = selector
                result['validation_reports'].append(validation_result)
                
                if validation_result['valid'] and validation_result['matches_expected']:
                    result['valid_selectors'].append(selector)
                    print_success(f"✓ Seletor {i+1} válido")
                else:
                    result['invalid_selectors'].append(selector)
                    print_warning(f"✗ Seletor {i+1} inválido: {validation_result.get('errors', [])}")
            
            result['validation_time'] = time.time() - validation_start
            result['total_time'] = time.time() - start_time
            
            print_success(f"Validação concluída: {len(result['valid_selectors'])}/{len(selectors)} seletores válidos")
            
        except Exception as e:
            print_error(f"Erro durante geração/validação: {str(e)}")
            result['error'] = str(e)
            result['total_time'] = time.time() - start_time
        
        return result
    
    def _extract_expected_info(self, element):
        """
        Extrai informações esperadas do elemento original
        
        Args:
            element: Elemento UI Automation
            
        Returns:
            dict: Informações que o seletor deve encontrar
        """
        try:
            return {
                'automation_id': getattr(element, 'AutomationId', '') or '',
                'name': getattr(element, 'Name', '') or '',
                'class_name': getattr(element, 'ClassName', '') or '',
                'control_type': getattr(element, 'ControlTypeName', '') or ''
            }
        except Exception:
            return {}
    
    def validate_single_selector(self, xml_selector, expected_element_info=None):
        """
        Valida um único seletor XML
        
        Args:
            xml_selector: String XML do seletor
            expected_element_info: Informações esperadas do elemento
            
        Returns:
            dict: Resultado detalhado da validação
        """
        print_info("Validando seletor individual...")
        
        start_time = time.time()
        validation_result = self.executor.validate_selector(
            xml_selector, 
            expected_element_info, 
            timeout=self.validation_timeout
        )
        
        validation_result['validation_time'] = time.time() - start_time
        execution_report = self.executor.get_execution_report()
        validation_result['execution_details'] = execution_report
        
        if validation_result['valid']:
            print_success("✓ Seletor válido")
        else:
            print_warning(f"✗ Seletor inválido: {validation_result.get('errors', [])}")
        
        return validation_result
    
    def test_selector_reliability(self, xml_selector, test_count=3):
        """
        Testa confiabilidade de um seletor executando múltiplas vezes
        
        Args:
            xml_selector: String XML do seletor
            test_count: Número de testes a executar
            
        Returns:
            dict: Relatório de confiabilidade
        """
        print_info(f"Testando confiabilidade do seletor ({test_count} execuções)...")
        
        results = []
        successful_executions = 0
        total_time = 0
        
        for i in range(test_count):
            start_time = time.time()
            
            try:
                element = self.executor.execute_selector(xml_selector, timeout=2)
                execution_time = time.time() - start_time
                total_time += execution_time
                
                if element:
                    successful_executions += 1
                    results.append({
                        'test': i + 1,
                        'success': True,
                        'execution_time': execution_time,
                        'element_found': True
                    })
                else:
                    results.append({
                        'test': i + 1,
                        'success': False,
                        'execution_time': execution_time,
                        'element_found': False,
                        'error': 'Elemento não encontrado'
                    })
                    
            except Exception as e:
                execution_time = time.time() - start_time
                total_time += execution_time
                results.append({
                    'test': i + 1,
                    'success': False,
                    'execution_time': execution_time,
                    'element_found': False,
                    'error': str(e)
                })
        
        reliability_percentage = (successful_executions / test_count) * 100
        average_time = total_time / test_count
        
        reliability_report = {
            'reliability_percentage': reliability_percentage,
            'successful_executions': successful_executions,
            'total_executions': test_count,
            'average_execution_time': average_time,
            'total_test_time': total_time,
            'individual_results': results,
            'classification': self._classify_reliability(reliability_percentage)
        }
        
        print_success(f"Confiabilidade: {reliability_percentage:.1f}% ({successful_executions}/{test_count})")
        print_info(f"Tempo médio: {average_time:.3f}s")
        
        return reliability_report
    
    def _classify_reliability(self, percentage):
        """
        Classifica confiabilidade baseada na porcentagem de sucesso
        
        Args:
            percentage: Porcentagem de sucesso
            
        Returns:
            str: Classificação da confiabilidade
        """
        if percentage >= 90:
            return "EXCELENTE"
        elif percentage >= 75:
            return "BOA"
        elif percentage >= 50:
            return "MODERADA"
        elif percentage >= 25:
            return "BAIXA"
        else:
            return "PÉSSIMA"
    
    def optimize_selectors(self, element, max_selectors=5):
        """
        Otimiza seletores retornando apenas os melhores e mais confiáveis
        
        Args:
            element: Elemento UI Automation
            max_selectors: Número máximo de seletores a retornar
            
        Returns:
            dict: Seletores otimizados com scores de confiabilidade
        """
        print_info("Otimizando seletores...")
        
        # Gera e valida todos os seletores
        result = self.generate_and_validate_selectors(element, validate_immediately=True)
        
        if not result['valid_selectors']:
            print_warning("Nenhum seletor válido encontrado")
            return {
                'optimized_selectors': [],
                'optimization_report': {
                    'total_generated': len(result.get('invalid_selectors', [])),
                    'total_valid': 0,
                    'optimization_time': result.get('total_time', 0)
                }
            }
        
        # Testa confiabilidade dos seletores válidos
        print_info("Testando confiabilidade dos seletores válidos...")
        
        selector_scores = []
        for i, selector in enumerate(result['valid_selectors']):
            print_info(f"Testando confiabilidade {i+1}/{len(result['valid_selectors'])}...")
            
            reliability = self.test_selector_reliability(selector, test_count=3)
            
            # Calcula score baseado em múltiplos fatores
            score = self._calculate_selector_score(selector, reliability)
            
            selector_scores.append({
                'selector': selector,
                'reliability': reliability,
                'score': score,
                'rank': 0  # Será definido após ordenação
            })
        
        # Ordena por score (maior é melhor)
        selector_scores.sort(key=lambda x: x['score'], reverse=True)
        
        # Adiciona ranking
        for i, item in enumerate(selector_scores):
            item['rank'] = i + 1
        
        # Retorna apenas os melhores
        optimized = selector_scores[:max_selectors]
        
        optimization_report = {
            'total_generated': len(result.get('valid_selectors', [])) + len(result.get('invalid_selectors', [])),
            'total_valid': len(result['valid_selectors']),
            'total_optimized': len(optimized),
            'optimization_time': result.get('total_time', 0),
            'best_reliability': optimized[0]['reliability']['reliability_percentage'] if optimized else 0,
            'worst_reliability': optimized[-1]['reliability']['reliability_percentage'] if optimized else 0
        }
        
        print_success(f"Otimização concluída: {len(optimized)} seletores selecionados")
        
        return {
            'optimized_selectors': optimized,
            'optimization_report': optimization_report
        }
    
    def _calculate_selector_score(self, selector, reliability_report):
        """
        Calcula score de qualidade para um seletor
        
        Args:
            selector: String XML do seletor
            reliability_report: Relatório de confiabilidade
            
        Returns:
            float: Score do seletor (0-100)
        """
        score = 0
        
        # Componente 1: Confiabilidade (40% do score)
        reliability_score = reliability_report['reliability_percentage'] * 0.4
        score += reliability_score
        
        # Componente 2: Velocidade (20% do score)
        avg_time = reliability_report['average_execution_time']
        if avg_time <= 0.5:
            speed_score = 20
        elif avg_time <= 1.0:
            speed_score = 15
        elif avg_time <= 2.0:
            speed_score = 10
        else:
            speed_score = 5
        score += speed_score
        
        # Componente 3: Robustez do seletor (40% do score)
        robustness_score = self._calculate_robustness_score(selector)
        score += robustness_score
        
        return min(score, 100)  # Máximo 100
    
    def _calculate_robustness_score(self, selector):
        """
        Calcula score de robustez baseado na estrutura do seletor
        
        Args:
            selector: String XML do seletor
            
        Returns:
            float: Score de robustez (0-40)
        """
        score = 0
        
        # AutomationId é mais robusto
        if 'automationId=' in selector:
            score += 25
        # Name + ControlType é moderadamente robusto
        elif 'name=' in selector and 'controlType=' in selector:
            score += 20
        # ClassName é menos robusto
        elif 'className=' in selector:
            score += 15
        else:
            score += 10
        
        # Janela específica adiciona robustez
        if '<Window title=' in selector:
            score += 10
        
        # Hierarquia adiciona contexto mas pode ser frágil
        if selector.count('<Element') > 1:
            score += 5
        
        return min(score, 40)  # Máximo 40