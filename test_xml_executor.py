"""
Script de teste para XMLSelectorExecutor
Testa funcionalidades básicas de execução de seletores XML
"""
import os
import sys
from xml_selector_executor import XMLSelectorExecutor
from utils import print_header, print_info, print_success, print_error, print_warning

def test_basic_functionality():
    """
    Testa funcionalidades básicas do XMLSelectorExecutor
    """
    print_header("TESTE DO XMLSelectorExecutor")
    
    executor = XMLSelectorExecutor()
    
    # Teste 1: Parse de XML válido
    print_info("Teste 1: Parse de XML válido")
    valid_xml = """
    <Selector>
        <Window title="Calculadora" />
        <Element automationId="num1Button" controlType="ButtonControl" />
    </Selector>
    """
    
    try:
        root = executor._parse_xml_selector(valid_xml)
        if root is not None:
            print_success("✓ Parse de XML válido funcionou")
        else:
            print_error("✗ Parse de XML válido falhou")
    except Exception as e:
        print_error(f"✗ Erro no teste 1: {str(e)}")
    
    # Teste 2: Parse de XML inválido
    print_info("Teste 2: Parse de XML inválido")
    invalid_xml = "<Selector><Window title='test'"
    
    try:
        root = executor._parse_xml_selector(invalid_xml)
        if root is None:
            print_success("✓ Parse de XML inválido detectado corretamente")
        else:
            print_error("✗ Parse de XML inválido não foi detectado")
    except Exception as e:
        print_success("✓ Parse de XML inválido gerou exceção esperada")
    
    # Teste 3: Validação de estrutura
    print_info("Teste 3: Validação de estrutura XML")
    wrong_root_xml = """
    <NotSelector>
        <Window title="Test" />
    </NotSelector>
    """
    
    try:
        root = executor._parse_xml_selector(wrong_root_xml)
        if root is None:
            print_success("✓ Validação de estrutura funcionou")
        else:
            print_error("✗ Estrutura inválida não foi detectada")
    except Exception as e:
        print_error(f"✗ Erro no teste 3: {str(e)}")
    
    # Teste 4: Relatório de execução
    print_info("Teste 4: Relatório de execução")
    try:
        report = executor.get_execution_report()
        if isinstance(report, dict):
            print_success("✓ Relatório de execução retornado")
            print_info(f"  Chaves do relatório: {list(report.keys())}")
        else:
            print_error("✗ Relatório não é um dicionário")
    except Exception as e:
        print_error(f"✗ Erro no teste 4: {str(e)}")
    
    # Teste 5: Tentativa de execução de seletor simples
    print_info("Teste 5: Execução de seletor (pode falhar se não houver janela)")
    simple_xml = """
    <Selector>
        <Window title="Notepad" />
    </Selector>
    """
    
    try:
        element = executor.execute_selector(simple_xml, timeout=1)
        report = executor.get_execution_report()
        
        if element:
            print_success("✓ Seletor executado com sucesso - elemento encontrado")
        else:
            print_warning("△ Seletor executado mas elemento não encontrado (normal se Notepad não estiver aberto)")
            
        print_info(f"  Tempo de execução: {report.get('execution_time', 0):.3f}s")
        print_info(f"  Passos executados: {len(report.get('steps', []))}")
        
    except Exception as e:
        print_error(f"✗ Erro no teste 5: {str(e)}")
    
    print_header("TESTES CONCLUÍDOS")

if __name__ == "__main__":
    # Verifica se está no Windows
    if os.name != 'nt':
        print_error("Este teste funciona apenas no Windows")
        sys.exit(1)
    
    test_basic_functionality()