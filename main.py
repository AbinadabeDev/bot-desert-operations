from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import re # Para parsear o tempo e valores em notação científica
import ast # Para avaliar expressões matemáticas

# COnfigurações configuráveis
URL_JOGO = 'https://desertoperations.fawkesgames.com/' # URL principal do game
TEMPO_PADRAO_ESPERA_SEGUNDOS = 60 # Tempo padrão para checar novamente se o temporizador falhar

# Lista de recursos
MAPA_RECURSOS = {
    "Dinheiro": "Money",
    "Ouro": "Gold",
    "Municao": "Munition",
    "Diesel":"Diesel",
    "Querosene": "Kerosene"
}

RECURSOS = ['Dinheiro', 'Ouro', 'Municao', 'Diesel' , 'Querosene']

print('--- Iniciando coleta de taxas de recursos ---')

def parse_notacao_cientifica(valor_str):
    '''Parseia strings para float'''
    try:
        # Substitui '^' por '**' e avalia como expressão python
        valor_str = valor_str.replace('^', '**').replace(' * ', ' * ').replace('10**', '1e') # Otimiza para float
        return float(ast.literal_eval(valor_str.split()[0] + 'e' + valor_str.split()[2])) if 'e' not in valor_str else float(valor_str)
    except:
        print(f'Erro ao parsear valor: {valor_str}')
        return 0.0

def obter_saldo_diamantes(driver):
    try:
        # Extrai o saldo de diamantes
        elemento_diamantes = WebDriverWait(driver, 10).until(EC.presence_of_element_located(By.XPATH, "//div[@id='resourcebar_diamonds']//span[@class='showTooltipDefault']"))
        texto_saldo = elemento_diamantes.text.strip()
        # Assuam que e um numero simples ou parseie se necessário
        saldo = int(re.sub(r'\D', '', texto_saldo)) # Remove não-dígitos
        print(f'Saldo de diamantes: {saldo}')
        return saldo
    except (NoSuchElementException, TimeoutException):
        print('Não conseguiu extrair saldo de diamantes. Ajuste o seletor.')
        return 0

def obter_tempo_restante_e_taxas(driver):
    try:
        # Clique no botão 'Premium'
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(By.XPATH, "//a[@id='menu_premium']"))
        driver.find_element(By.XPATH, "//a[@id='menu_premium']").click()

        # Clique em 'Troca de Recursos'
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[span[text()='Troca de Recursos']]")))
        driver.find_element(By.XPATH, "//a[span[text()='Troca de Recursos']]").click()

        # Extrai os valores atuais para cada recurso
        taxas = {}
        for recurso in RECURSOS:
            try:
                # Pega a palavra chave em ingles do mapa
                id_palavra_chave = MAPA_RECURSOS[recurso]

                xpath_direto_para_o_valor = f"//img[@title='{recurso}']/ancestor::div[contains(@class, 'premiumResourceGridItem')]//span[contains(@id, 'sliderAmountDiaExchange{id_palavra_chave}')]"
                elemento_valor = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath_direto_para_o_valor)))

                valor_bruto = elemento_valor.text.strip()
                taxas[recurso] = parse_notacao_cientifica(elemento_valor.text.strip())
                print(f'Sucesso para recurso: {recurso}: {taxas[recurso]}')
            except Exception as e:
                print(f'!!! Falha ao processar o recurso: {recurso}. Verifique o nome no mapa ou o HTML. Erro: {e}')

        print('\n--- Coleta finalizada ---')
        print(taxas)

        print('Taxas atuais por 1 diamante:')
        for rec, taxa in taxas.items():
            print(f'{rec}: {taxa:.2e}') # Mostra a notação científica

        # Clique em mais informações para exibir
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='showAccountValueGraph']"))) # Ajuste texto/XPath
        driver.find_element(By.XPATH, "//*[@id='showAccountValueGraph']").click()
        try:
            # XPath para encontrar o contador pela sua classe única
            xpath_contador = "//div[contains(@class, 'calculation-countdown')]"
            # Espera o elemento aparecer e o captura
            elemento_temporizador = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, xpath_contador))) # Ajuste elemento ID/XPATH para o elemento com o tempo
            # Pega o valor do atributo 'data-countdown' (será uam string '1759')
            segundos_restantes_str = elemento_temporizador.get_attribute('data-countdown')
            # Converte a string para um número inteiro
            segundos_para_esperar = int(segundos_restantes_str)

            print(f'Próximo cálculo em {segundos_para_esperar} segundos')
            print('A automação irá pausar agora e continuar após o tempo acabar...')

            # Pausa a execução do script pelo número exato de segundos
            # (Adicionamos +5 seguindo de margem de segurança para garantir)
            time.sleep(segundos_para_esperar + 5)

            print('Tempo de espera finalizado! Continuando a execução do script...')
        except Exception as e:
            print(f'!!! Não foi possível encontrar o contador de tempo. Erro: {e}')

        # Parseia o tempo (ex: 'Atualiza em 5 minutos' - ajuste regex conforme o formato exato)
        correspondencia = re.search(r'(\d+)\s*(minuto|minutos|hora|horas)', elemento_temporizador)
        if correspondencia:
            valor_tempo = int(correspondencia.group(1))
            unidade = correspondencia.group(2).lower()
            if 'hora' in unidade:
                segundos_restantes = valor_tempo * 3600
            else:
                segundos_restantes = valor_tempo * 60
            print(f'Tempo restante para atualização: {segundos_restantes} segundos')
            return segundos_restantes, taxas
        else:
            print('Formato de tempo não reconhecido. Usando wait padrão.')
            return TEMPO_PADRAO_ESPERA_SEGUNDOS, taxas
    except (NoSuchElementException, TimeoutException):
        print('Não conseguiu extrair tempo ou taxas. Usando wait padrão.')
        return TEMPO_PADRAO_ESPERA_SEGUNDOS, {}

def efetuar_troca(driver, recurso, quantidade):
    try:
        # Clique no botão HQ para dar um refresh no mapa (ajuste o XPath)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='menu_hq']"))) # Ajuste texto/XPath
        driver.find_element(By.XPATH, "//*[@id='menu_hq']").click() # ajuste texto/XPath
        time.sleep(2) # pequeno delay para o refresh do mapa

        # Acessa novamente Premium > Troca de Recursos
        driver.find_element(By.XPATH, "//a[@id='menu_premium']").click()
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[span[text()='Troca de Recursos']]")))
        driver.find_element(By.XPATH, "//a[span[text()='Troca de Recursos']]").click()

        # Seleciona o recurso, insere quantidade e confirma (ajuste XPaths)
        # Assuma que cada recurso tem seu próprio input e botão Troca
        secao_recurso = driver.find_element(By.XPATH, f"//div[contains(@class, 'premiumResourceGridItemValue') and contains(., '{recurso}')]/ancestor::div[contains(@class, 'premiumResourceGridItem')]") # Ajuste para seção do recurso
        elemento_input = secao_recurso.find_element(By.XPATH, ".//input[@type='text']") # Ajuste ID; pode ser por recurso
        elemento_input.clear()
        elemento_input.send_keys(str(quantidade))

        botao_troca = secao_recurso.find_element(By.XPATH, ".//a[contains(., 'Troca')]") # Botão de troca na seção
        botao_troca.click()

        print(f'Troca de {quantidade} diamantes por {recurso} realizada.')
    except (NoSuchElementException, TimeoutException):
        print('Erro ao realizar troca. Ajuste seletores.')

def principal():
    opcoes = webdriver.ChromeOptions()
    opcoes.add_argument('--headless') # Descomentar para rodar sem janela (depois de testar)
    driver = webdriver.Chrome(options=opcoes)

    driver.get(URL_JOGO)
    input('Por favor, logue manualmente ao navegador aberto e pressione ENTER quando estiver pronto para continuar...')

    while True:
        # Obtém o saldo de diamantes
        saldo_diamantes = obter_saldo_diamantes(driver)

        # Obtém o tempo restante e taxas atuais
        tempo_espera, taxas_atuais = obter_tempo_restante_e_taxas(driver)
        if tempo_espera > 0:
            time.sleep(tempo_espera + 10) # Espera o tempo +10s buffer para garantir atualização

        # Após espera, mostra taxas atualizadas e pede confirmação para troca
        _, taxas_atualizadas = obter_tempo_restante_e_taxas(driver) # Re-checa para taxas pós-atualização
        print('Taxas atualizadas após espera:')
        for rec, taxa in taxas_atualizadas.items():
            print(f'{rec}: {taxa:.2e}')

        # Rede de segurança: Espera comando do usuário
        confirmar = input('Deseja realizar uma troca? (sim/não): ').lower()
        if confirmar == 'sim':
            recurso = input(f'Escolha o recurso ({', '.join(RECURSOS)}): ')
            if recurso in RECURSOS:
                quantidade = input('Digite a quantidade de diamantes: ')
                # Verifica se a quantidade é menor ou igual ao saldo
                if int(quantidade) > saldo_diamantes:
                    print('Quantidade excede o saldo de diamantes. Cancelando')
                else:
                    efetuar_troca(driver, recurso,quantidade)
            else:
                print('Recurso inválido.')
        else:
            print('Troca cancelada. Continuando monitoramento...')

        # Opcional: Pequeno delay antes do próximo ciclo
        time.sleep(60) # Ajuste para evitar loops muito rápidos

    driver.quit()

if __name__ == '__main__':
    principal()