# -*- coding: utf-8 -*-
"""
Este script implementa um assistente de automação para o jogo de estratégia
online Desert Operations. Utilizando Selenium, ele navega até a seção de
troca de recursos premium, extrai informações em tempo real sobre as taxas de
câmbio e o tempo de atualização, e fornece uma interface de console interativa
para que o usuário possa realizar trocas de forma assistida.

Autor: [Seu Nome ou Apelido]
Data de Criação: [Data de Início do Projeto]
Versão: 1.0
LinkedIn: https://www.linkedin.com/help/linkedin/answer/a1338223/como-se-cadastrar-no-linkedin?lang=pt
GitHub: https://docs.github.com/pt/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github

Principais Funcionalidades:
- Login manual seguido por automação da sessão.
- Navegação complexa através de iframes aninhados.
- Extração de dados dinâmicos da página (taxas de câmbio e timers).
- Interface de linha de comando (CLI) para interação do usuário.
- Simulação de interações do usuário, como uso de teclado para ajustar sliders.
- Gerenciamento de estado da interface para lidar com pop-ups e painéis dinâmicos.
"""

# Importações de bibliotecas padrão e de terceiros
import time
import logging
import locale
import random

# Importações específicas do Selenium
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# ============================
# MÓDULO DE CONFIGURAÇÃO
# ============================

# URL base do jogo.
URL_JOGO = "https://desertoperations.fawkesgames.com/"

# Lista de recursos disponíveis para troca, na ordem em que aparecem na interface.
RECURSOS = ["Dinheiro", "Ouro", "Munição", "Diesel", "Querosene"]

# Configuração do sistema de logging para feedback claro no console.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# ============================
# MAPEAMENTO DE ELEMENTOS (Locators)
# ============================

# Dicionário gerado dinamicamente para armazenar os XPaths dos elementos da página.
# Esta abordagem torna o código mais limpo e fácil de manter.
XPATHS_RECURSOS = {}
for recurso in RECURSOS:
    # XPath base para localizar o container de cada recurso.
    # A robustez é garantida por buscar um container que TENHA uma imagem com o título esperado.
    bloco_recurso = f"//div[contains(@class, 'premiumResourceGridItem') and .//img[@title='{recurso}']]"

    XPATHS_RECURSOS[recurso] = {
        "rate": f"{bloco_recurso}//span[contains(@class, 'tooltipExtention')]",
        "quantity": f"{bloco_recurso}//span[starts-with(@id, 'sliderCountDiaExchange')]",
        "exchange": f"{bloco_recurso}//a[contains(@class, 'getPremiumResources')]",
    }


# ============================
# FUNÇÕES UTILITÁRIAS
# ============================

def esperar_pelo_texto_do_timer(driver):
    """
    Uma condição de espera personalizada para o WebDriverWait.

    Aguarda até que o elemento do timer esteja presente e seu texto contenha
    uma unidade de tempo ('h', 'm', ou 's'), indicando que foi carregado.

    Retorna o elemento quando a condição é satisfeita, ou False caso contrário.
    """
    try:
        # Localiza o elemento do timer a cada verificação
        element = driver.find_element(By.XPATH, "//span[contains(@class, 'calculation-countdown')]")

        # Verifica se o texto é válido (não vazio, não "-", e contém uma unidade de tempo)
        texto = element.text.lower()
        if texto and texto.strip() != '-' and ('h' in texto or 'm' in texto or 's' in texto):
            return element  # Retorna o próprio elemento em caso de sucesso
        return False
    except NoSuchElementException:
        return False


def parse_tempo_para_segundos(texto_tempo):
    """
    Converte uma string de tempo (ex: '25m 10s') para um total de segundos,
    de forma mais robusta.
    """
    if not isinstance(texto_tempo, str):
        return 0

    total_segundos = 0
    # Garante que o texto esteja em minúsculas e remove espaços extras
    partes = texto_tempo.strip().lower().split(' ')

    for parte in partes:
        try:
            if 'h' in parte:
                # Remove o 'h' e converte para número
                total_segundos += int(parte.replace('h', '')) * 3600
            elif 'm' in parte:
                total_segundos += int(parte.replace('m', '')) * 60
            elif 's' in parte:
                total_segundos += int(parte.replace('s', ''))
        except (ValueError, TypeError):
            # Se uma parte não puder ser convertida (ex: ''), ignora e continua
            logger.warning(f"Não foi possível interpretar a parte do tempo: '{parte}'")
            continue

    return total_segundos


def parse_valor_limpo(valor_str):
    """
    Converte uma string numérica formatada em um valor float.

    Remove os pontos utilizados como separadores de milhar antes de converter,
    garantindo que a conversão para float seja bem-sucedida.

    Args:
        valor_str (str): A string numérica a ser convertida (ex: '1.060.211').

    Returns:
        float: O valor numérico convertido. Retorna 0.0 em caso de erro.
    """
    try:
        # Remove os pontos (separador de milhar) antes de converter.
        valor_limpo = valor_str.replace('.', '')
        return float(valor_limpo)
    except (ValueError, TypeError) as e:
        logger.error(f"Erro ao converter o valor '{valor_str}': {e}")
        return 0.0


def formatar_segundos(total_segundos):
    """
    Converte um total de segundos para o formato de tempo HH:MM:SS.

    Args:
        total_segundos (int): A quantidade total de segundos.

    Returns:
        str: A string formatada como 'HH:MM:SS'.
    """
    if not isinstance(total_segundos, (int, float)) or total_segundos < 0:
        return "00:00:00"

    horas, rem = divmod(total_segundos, 3600)
    minutos, segundos = divmod(rem, 60)
    return f"{int(horas):02d}:{int(minutos):02d}:{int(segundos):02d}"


def validar_entrada_numerica(prompt, minimo=1, maximo=None):
    """
    Solicita e valida uma entrada numérica do usuário dentro de um intervalo.
    Agora lida com números formatados com pontos (ex: 1.000).
    """
    while True:
        try:
            entrada = input(prompt).strip()
            if entrada.lower() in ['sair', 'cancelar']:
                return None

            # --- A CORREÇÃO ESTÁ AQUI ---
            # Remove os pontos da string antes de converter para inteiro.
            entrada_sem_pontos = entrada.replace('.', '')

            valor_int = int(entrada_sem_pontos)

            if valor_int < minimo:
                print(f"Valor inválido. O mínimo é {minimo:n}.")
                continue

            if maximo is not None and valor_int > maximo:
                print(f"Valor inválido. O máximo é {maximo:n}.")
                continue

            return valor_int
        except ValueError:
            print("Entrada inválida. Por favor, digite apenas números.")


# ============================
# FUNÇÕES DE INTERAÇÃO (Selenium)
# ============================


def fechar_lightbox(driver):
    """Fecha um pop-up (lightbox) e retorna o foco do driver para o iframe principal do jogo."""
    try:
        # Tenta clicar no botão de fechar primeiro (espera curta)
        botao_fechar = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.ID, "lightBoxClose"))
        )
        botao_fechar.click()
        logger.info("Lightbox temporário fechado via botão na aba principal.")
    except Exception:
        # Se falhar, tenta uma abordagem alternativa enviando a tecla ESCAPE
        try:
            logger.warning("Não foi possível fechar via botão, tentando com a tecla ESCAPE.")
            ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            logger.info("Comando ESCAPE enviado para fechar o lightbox.")
        except Exception as e2:
            logger.error(f"Falha ao tentar fechar o lightbox com ESCAPE: {e2}")


def navegar_para_troca_recursos(driver):
    """
    Navega da tela principal do jogo até a interface de troca de recursos.

    Este processo envolve a manipulação de iframes aninhados, uma técnica
    essencial para automação de aplicações web complexas.

    Args:
        driver (webdriver): A instância do navegador Selenium.

    Returns:
        bool: True se a navegação for bem-sucedida, False caso contrário.
    """
    try:
        # Garante que o driver esteja no contexto principal antes de começar.
        driver.switch_to.default_content()
        # Entra no iframe principal do jogo.
        WebDriverWait(driver, 15).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, "game-frame"))
        )
        logger.info("Contexto do driver alterado para 'game-frame'.")

        # Clica no botão "Premium" para abrir o menu correspondente.
        botao_premium = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.ID, "menu_premium"))
        )
        driver.execute_script("arguments[0].click();", botao_premium)
        logger.info("Menu 'Premium' aberto.")

        # O menu abre um novo iframe DENTRO do 'game-frame'.
        # O driver precisa mudar seu foco para este novo iframe.
        WebDriverWait(driver, 20).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, "lightBoxFrame"))
        )
        logger.info("Contexto do driver alterado para 'lightBoxFrame' aninhado.")

        # Dentro do 'lightBoxFrame', clica no link para a troca de recursos.
        resource_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='premium_cash.php?section=ress']"))
        )
        driver.execute_script("arguments[0].click();", resource_button)
        logger.info("Acessando a tela de Troca de Recursos.")

        # Valida se a tela carregou verificando a presença de um elemento chave.
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//img[@title='Dinheiro']"))
        )
        logger.info("Tela de Troca de Recursos carregada com sucesso.")
        return True

    except TimeoutException as e:
        logger.error(f"Tempo esgotado durante a navegação para a troca de recursos: {e}")
        return False
    except Exception as e:
        logger.error(f"Erro inesperado durante a navegação: {e}")
        return False


def abrir_e_focar_aba_premium(driver):
    """
    Captura a URL do conteúdo premium, abre em uma nova aba, e move o foco do driver.
    """
    try:
        logger.info("Iniciando o processo de abertura da aba premium (Método de Captura de URL)...")
        aba_original = driver.current_window_handle

        # ETAPA 1: Entra no iframe e clica em 'Premium' para fazer o lightbox aparecer
        driver.switch_to.default_content()
        WebDriverWait(driver, 15).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, "game-frame"))
        )
        botao_premium = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.ID, "menu_premium"))
        )
        botao_premium.click()

        # ETAPA 2: 'Espiona' o iframe que acabou de aparecer e captura sua URL (src)
        logger.info("Aguardando e capturando a URL do iframe premium...")
        iframe_premium = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "lightBoxFrame"))
        )
        url_premium_capturada = iframe_premium.get_attribute('src')

        if not url_premium_capturada:
            logger.error("Não foi possível capturar a URL do iframe.")
            return None

        # ETAPA 3: Limpa a tela original fechando o lightbox que foi aberto
        fechar_lightbox(driver)
        driver.switch_to.default_content()  # Garante que o foco está no topo

        # ETAPA 4: Abre a URL capturada em uma nova aba
        driver.switch_to.new_window('tab')
        driver.get(url_premium_capturada)
        logger.info(f"Nova aba aberta com a URL capturada: {url_premium_capturada}")

        # ETAPA 5: Na nova aba, navega para a tela final de 'Troca de Recursos'
        resource_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='premium_cash.php?section=ress']"))
        )
        resource_button.click()

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//img[@title='Dinheiro']"))
        )
        logger.info("Tela de Troca de Recursos carregada e validada na nova aba.")

        return aba_original

    except Exception as e:
        logger.error(f"Não foi possível abrir ou focar na nova aba premium: {e}")
        return None


def fechar_lightbox(driver):
    """
    Fecha um pop-up (lightbox) e retorna o foco do driver para o iframe principal do jogo.

    Args:
        driver (webdriver): A instância do navegador Selenium.
    """
    try:
        # Retorna o foco do iframe do pop-up para o iframe pai ('game-frame').
        driver.switch_to.parent_frame()

        # Tenta localizar e clicar no botão de fechar do pop-up.
        botao_fechar = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "lightBoxClose"))
        )
        botao_fechar.click()
        logger.info("Lightbox fechado com sucesso.")
    except Exception as e:
        logger.warning(f"Não foi possível fechar o lightbox da forma padrão: {e}")


def ajustar_slider(driver, recurso, quantidade_alvo):
    """
    Ajusta o slider de um recurso para uma quantidade específica simulando as setas do teclado.

    Args:
        driver (webdriver): A instância do navegador Selenium.
        recurso (str): O nome do recurso a ser ajustado.
        quantidade_alvo (int): A quantidade de diamantes desejada.

    Returns:
        bool: True se o ajuste for bem-sucedido, False caso contrário.
    """
    try:
        # Mapeia o nome do recurso para o sufixo do ID usado no HTML.
        recurso_id_map = {
            "Dinheiro": "Money", "Ouro": "Gold", "Munição": "Ammunition",
            "Diesel": "Diesel", "Querosene": "Cerosin"
        }
        recurso_suffix = recurso_id_map[recurso]
        slider_id = f"playzoSliderDiaExchange{recurso_suffix}"
        span_id = f"sliderCountDiaExchange{recurso_suffix}"

        # Localiza o controle deslizante (handle) que receberá os comandos do teclado.
        slider_handle = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f"#{slider_id} .playzo-slider-button"))
        )

        # Obtém o valor atual para calcular a diferença.
        valor_atual_str = driver.find_element(By.ID, span_id).text
        quantidade_atual = int(valor_atual_str.replace('.', ''))
        diferenca = quantidade_alvo - quantidade_atual

        if diferenca == 0:
            logger.info(f"O slider de {recurso} já está na posição desejada.")
            return True

        logger.info(f"Ajustando slider de {recurso} de {quantidade_atual} para {quantidade_alvo}...")

        # Determina qual tecla (direita ou esquerda) e quantas vezes pressionar.
        tecla = Keys.ARROW_RIGHT if diferenca > 0 else Keys.ARROW_LEFT

        # Envia a sequência de teclas de uma só vez para maior eficiência.
        slider_handle.send_keys(tecla * abs(diferenca))

        # Valida se o valor foi alterado corretamente.
        time.sleep(0.5)  # Pausa para a interface gráfica atualizar.
        valor_final_str = driver.find_element(By.ID, span_id).text
        if int(valor_final_str.replace('.', '')) == quantidade_alvo:
            logger.info("Slider ajustado com sucesso.")
            return True
        else:
            logger.warning(f"O valor do slider ({valor_final_str}) não correspondeu ao alvo ({quantidade_alvo}).")
            return False

    except Exception as e:
        logger.error(f"Erro ao ajustar o slider via teclado: {e}")
        return False


def efetuar_troca_automatica(driver, recurso, quantidade):
    """
    Realiza a troca de forma totalmente automática, confirmando todas as etapas.
    """
    try:
        logger.info(f"Iniciando troca automática: {quantidade} diamantes por {recurso}.")

        if not ajustar_slider(driver, recurso, int(quantidade)):
            logger.error(f"Falha ao ajustar o slider para {recurso}.")
            return False

        driver.find_element(By.XPATH, XPATHS_RECURSOS[recurso]["exchange"]).click()

        # Aguarda e clica no "OK" da primeira caixa de diálogo
        ok_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "messageBoxLeftButton"))
        )
        ok_button.click()

        # Aguarda e clica no "Fechar" da caixa de diálogo de sucesso
        fechar_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#messageBoxAlertButton .button"))
        )
        fechar_button.click()

        # Aguarda a finalização
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.ID, "messageBoxOverlay"))
        )
        logger.info(f"Troca por {recurso} concluída com sucesso.")
        return True

    except Exception as e:
        logger.error(f"Ocorreu um erro durante a troca automática por {recurso}: {e}")
        return False


# ============================
# FUNÇÕES DE LÓGICA DE NEGÓCIO
# ============================

def obter_saldo_diamantes(driver):
    """Obtém o saldo de diamantes lendo o atributo 'max' do slider na aba atual."""
    try:
        slider_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "playzoSliderDiaExchangeMoney"))
        )
        saldo_diamantes_str = slider_container.get_attribute("max")
        return int(saldo_diamantes_str) if saldo_diamantes_str and saldo_diamantes_str.isdigit() else 0
    except Exception as e:
        logger.error(f"Não foi possível obter o saldo de diamantes na aba premium: {e}")
        return 0


def obter_dados_da_tela(driver):
    """
    Coleta todas as informações dinâmicas da tela de troca de recursos.
    Usa uma espera inteligente para garantir a captura correta do timer.
    """
    taxas = {}
    for recurso in RECURSOS:
        try:
            elemento_valor = driver.find_element(By.XPATH, XPATHS_RECURSOS[recurso]["rate"])
            valor_do_atributo = elemento_valor.get_attribute("title")
            taxas[recurso] = parse_valor_limpo(valor_do_atributo)
        except NoSuchElementException:
            taxas[recurso] = 0.0

    segundos_restantes = 0
    try:
        graph_panel = driver.find_element(By.ID, "premiumGraph")
        if not graph_panel.is_displayed():
            botao_grafico = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "showAccountValueGraph")))
            driver.execute_script("arguments[0].click();", botao_grafico)
            WebDriverWait(driver, 5).until(EC.visibility_of(graph_panel))

        # --- MUDANÇA PRINCIPAL: Usa a nova função de espera inteligente ---
        # Esta linha substitui as duas esperas anteriores por uma única e mais robusta.
        logger.info("Aguardando o valor final do timer ser carregado...")
        elemento_temporizador = WebDriverWait(driver, 15).until(esperar_pelo_texto_do_timer)

        texto_do_timer = elemento_temporizador.text
        logger.info(f"Texto do timer capturado com sucesso: '{texto_do_timer}'")
        segundos_restantes = parse_tempo_para_segundos(texto_do_timer)
        # -----------------------------------------------------------------

    except Exception:
        logger.warning("Não foi possível obter o timer na atualização.")

    return taxas, segundos_restantes


def atualizar_cambio_via_hq(driver):
    """
    Executa um "hard refresh" das taxas de câmbio.

    Simula o fluxo de um usuário: fecha a janela de troca, navega para o
    Quartel-General (HQ) para forçar uma atualização de estado com o servidor,
    e então reabre a janela de troca.

    Args:
        driver (webdriver): A instância do navegador Selenium.

    Returns:
        bool: True se a atualização for bem-sucedida, False caso contrário.
    """
    try:
        logger.info("Iniciando atualização completa das taxas de câmbio...")

        fechar_lightbox(driver)

        logger.info("Navegando para o Quartel-General (HQ) para recarregar dados.")
        hq_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.ID, "menu_hq"))
        )
        hq_button.click()
        time.sleep(2)  # Pausa para garantir que a atualização seja processada.

        logger.info("Retornando para a tela de troca de recursos...")
        if not navegar_para_troca_recursos(driver):
            logger.error("Falha ao retornar para a tela de troca após atualização.")
            return False

        logger.info("Atualização completa concluída.")
        return True

    except Exception as e:
        logger.error(f"Ocorreu um erro durante a atualização via HQ: {e}")
        return False


# ============================
# FUNÇÃO PRINCIPAL DE EXECUÇÃO
# ============================

def principal():
    """
    Função principal que orquestra o bot de forma totalmente autônoma,
    operando em ciclos de espera e troca.
    """
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    except locale.Error:
        logger.warning("Locale 'pt_BR.UTF-8' não encontrado.")

    logger.info("=" * 50)
    logger.info("BOT AUTÔNOMO DE TROCAS PARA DESERT OPERATIONS")
    logger.info("=" * 50)

    opcoes = webdriver.ChromeOptions()
    opcoes.add_argument('--log-level=3')
    opcoes.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=opcoes)
    aba_original = None

    try:
        driver.get(URL_JOGO)
        input("\n>>> Faça o login no jogo e pressione ENTER para iniciar o bot...\n")

        aba_original = abrir_e_focar_aba_premium(driver)
        if not aba_original:
            return

        # --- FASE DE CONFIGURAÇÃO INICIAL (REQUISITO 1) ---
        saldo_inicial = obter_saldo_diamantes(driver)
        logger.info(f"Saldo atual de diamantes: {saldo_inicial:n}")
        quantidade_padrao_de_troca = validar_entrada_numerica(
            f"Defina a quantidade padrão de diamantes para usar em cada troca (Máx: {saldo_inicial:n}): ",
            minimo=1,
            maximo=saldo_inicial
        )
        if quantidade_padrao_de_troca is None:
            logger.info("Nenhuma quantidade definida. Encerrando.")
            return

        logger.info(f"Quantidade padrão definida para {quantidade_padrao_de_troca:n} diamantes por recurso.")
        logger.info("Iniciando o primeiro ciclo do bot...")

        # --- LOOP DE CICLO AUTÔNOMO ---
        ciclo_num = 1
        while True:
            logger.info("=" * 50)
            logger.info(f"INICIANDO CICLO DE OPERAÇÃO Nº {ciclo_num}")

            # 1. FASE DE ESPERA (REQUISITO 3)
            logger.info("Verificando o temporizador para a próxima atualização de câmbio...")
            _, segundos_restantes = obter_dados_da_tela(driver)

            if segundos_restantes > 0:
                tempo_formatado = formatar_segundos(segundos_restantes)
                logger.info(f"Aguardando {tempo_formatado} para a atualização das taxas...")
                # Adiciona um buffer de 15s para garantir que o servidor atualizou
                time.sleep(segundos_restantes + 15)

            # 2. FASE DE ATUALIZAÇÃO
            logger.info("Tempo esgotado. Recarregando a página para obter novas taxas...")
            driver.refresh()
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//img[@title='Dinheiro']"))
            )
            logger.info("Página atualizada com novas taxas de câmbio.")

            # 3. FASE DE TROCAS EM FILA (REQUISITO 2)
            logger.info("-" * 50)
            logger.info("Iniciando a fila de trocas automáticas...")

            for recurso in RECURSOS:
                saldo_atual = obter_saldo_diamantes(driver)
                if saldo_atual < quantidade_padrao_de_troca:
                    logger.warning(
                        f"Saldo de diamantes ({saldo_atual:n}) insuficiente para a troca de {quantidade_padrao_de_troca:n}. Encerrando fila de trocas deste ciclo.")
                    break

                if efetuar_troca_automatica(driver, recurso, quantidade_padrao_de_troca):
                    # Pausa entre as trocas para não sobrecarregar o servidor
                    time.sleep(random.randint(3, 7))
                else:
                    logger.error(f"Falha na troca por {recurso}. Pulando para o próximo recurso.")
                    continue

            logger.info("Fila de trocas do ciclo atual finalizada.")
            ciclo_num += 1

    except KeyboardInterrupt:
        logger.info("Bot interrompido pelo usuário.")
    finally:
        logger.info("Encerrando o bot...")
        if aba_original and len(driver.window_handles) > 1:
            try:
                driver.close()
                driver.switch_to.window(aba_original)
            except Exception:
                pass
        driver.quit()


if __name__ == "__main__":
    principal()
