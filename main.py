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
RECURSOS = ['Dinheiro', 'Ouro', 'Municao', 'Diesel', 'Querosene']

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
        # Extrai o saldo de diamantes ( - ajustar os XPaths)
        elemento_diamantes = WebDriverWait(driver, 10).until(EC.presence_of_element_located(By.XPATH, "//div[contains(@class, 'diamonds-balance')]"))
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
        # Clique no botão 'Premium' (ajuste XPath)
        WebDriverWait(driver, 10).until((EC.element_to_be_clickable(By.XPATH, "//button[contains(text(), 'Premium'")))
        driver.find_element(By.XPATH, "//button[contains(text(), 'Premium'").click()

        # Clique em 'Troca de Recursos' (ajuste XPath)
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Troca de Recursos')], 'Troca de Recursos'")))
        driver.find_element(By.XPATH, "//a[contains(text(), 'Troca de Recursos'").click()

        # Extrai os valores atuais para cada recurso (ajuste XPaths para os elementos)
        taxas = {}
        for recurso in RECURSOS:
            elemento_valor = driver.find_element(By.XPATH, f"//div[, '{recurso}')]/preceding-sibling::div[contains(text(), '*')]")
            taxas[recurso] = parse_notacao_cientifica(elemento_valor.text.strip())

        print('Taxas atuais por 1 diamante:')
        for rec, taxa in taxas.items():
            print(f'{rec}: {taxa:.2e}') # Mostra a notação científica

        # Clique em mais informações para exibir
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Mais Informações')]"))) # Ajuste texto/XPath
        driver.find_element(By.XPATH, "//button[contains(text(), 'Mais Informações')]").click()

        # Extrai o elemento temporizador (após o click, assume que aparece em um novo elemento: ajustar XPath)
        elemento_temporizador = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "timer-info"))) # Ajuste elemento ID/XPATH para o elemento com o tempo
        texto_temporizador = elemento_temporizador.text.strip()

        # Parseia o tempo (ex: 'Atualiza em 5 minutos' - ajuste regex conforme o formato exato)
        correspondencia = re.search(r'(\d+)\s*(minuto|minutos|hora|horas)', texto_temporizador)
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
            print(f'Tempo restante para atualização: {segundos_restantes} segundos.')
            return TEMPO_PADRAO_ESPERA_SEGUNDOS, taxas
    except (NoSuchElementException, TimeoutException):
        print('Não conseguiu extrair tempo ou taxas. Usando wait padrão.')
        return TEMPO_PADRAO_ESPERA_SEGUNDOS, {}

def efetuar_troca(driver, recurso, quantidade):
    try:
        # Clique no botão HQ para dar um refresh no mapa (ajuste o XPath)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'HQ"))) # Ajuste texto/XPath