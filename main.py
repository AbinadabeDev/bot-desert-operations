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

# Importações específicas do Selenium
from selenium import webdriver
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
            entrada_sem_pontos = entrada.replace('.', ' ')

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
    Abre a tela de troca de recursos em uma nova aba e move o foco do driver para ela.

    Args:
        driver (webdriver): A instância do navegador Selenium.

    Returns:
        str or None: O handle da aba original do jogo, ou None em caso de falha.
    """
    try:
        logger.info("Iniciando o processo de abertura da aba premium...")
        # Salva o identificador da aba original (mapa do jogo)
        aba_original = driver.current_window_handle

        # Constrói a URL direta para a troca de recursos.
        # Isso evita a necessidade de clicar em múltiplos menus.
        url_base = "/".join(driver.current_url.split("/")[:-1])
        url_premium = f"{url_base}/premium_cash.php?section=ress"

        # Abre a URL em uma nova aba
        driver.switch_to.new_window('tab')
        driver.get(url_premium)

        logger.info(f"Nova aba aberta com sucesso no endereço: {url_premium}")

        # Valida se a nova aba carregou corretamente
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


def efetuar_troca_na_tela(driver, recurso, quantidade):
    """
    Executa o fluxo completo de uma troca na tela de recursos, incluindo as caixas de diálogo.

    Args:
        driver (webdriver): A instância do navegador Selenium.
        recurso (str): O nome do recurso a ser trocado.
        quantidade (int): A quantidade de diamantes a ser utilizada.

    Returns:
        bool: True se a troca for confirmada e bem-sucedida, False caso contrário.
    """
    try:
        if not ajustar_slider(driver, recurso, int(quantidade)):
            return False

        # Clica no botão "Troca" inicial.
        botao_troca = driver.find_element(By.XPATH, XPATHS_RECURSOS[recurso]["exchange"])
        botao_troca.click()

        # Aguarda a primeira caixa de diálogo (confirmação).
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "messageBoxOverlay"))
        )
        logger.info("Caixa de diálogo de confirmação exibida.")

        # Solicita a confirmação do usuário.
        while True:
            confirmacao = input("Confirmar a troca? [1] Sim, [0] Não: ").strip()
            if confirmacao == '1':
                logger.info("Confirmando a troca...")
                ok_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "messageBoxLeftButton"))
                )
                ok_button.click()

                # Aguarda a segunda caixa de diálogo (sucesso) e a fecha.
                logger.info("Aguardando confirmação de sucesso do servidor...")
                fechar_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "#messageBoxAlertButton .button"))
                )
                logger.info("Troca realizada com sucesso!")
                fechar_button.click()

                resultado_final = True
                break
            elif confirmacao in ['0', '00']:
                logger.info("Troca cancelada pelo usuário.")
                cancel_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "messageBoxRightButton"))
                )
                cancel_button.click()
                resultado_final = False
                break
            else:
                print("Opção inválida. Por favor, digite 1 para Sim ou 0 para Não.")

        # Aguarda o desaparecimento do overlay da caixa de diálogo.
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.ID, "messageBoxOverlay"))
        )
        return resultado_final

    except Exception as e:
        logger.error(f"Ocorreu um erro durante a operação de troca: {e}")
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

    Isso inclui as taxas de câmbio de todos os recursos e o tempo restante
    no contador de atualização.

    Args:
        driver (webdriver): A instância do navegador Selenium.

    Returns:
        tuple: Uma tupla contendo um dicionário de taxas e os segundos restantes.
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

        elemento_temporizador = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'calculation-countdown')]"))
        )
        WebDriverWait(driver, 10).until(lambda d: elemento_temporizador.text.strip() != "-")

        future_timestamp = int(elemento_temporizador.get_attribute('data-countdown'))
        current_timestamp = int(time.time())
        segundos_restantes = future_timestamp - current_timestamp
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
    """Função principal que orquestra a execução do assistente de automação em uma aba dedicada."""
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    except locale.Error:
        logger.warning("Locale 'pt_BR.UTF-8' não encontrado. Usando formatação padrão.")

    logger.info("=" * 50)
    logger.info("ASSISTENTE DE TROCAS PARA DESERT OPERATIONS (MODO ABA DEDICADA)")
    logger.info("=" * 50)

    opcoes = webdriver.ChromeOptions()
    opcoes.add_argument('--log-level=3')
    opcoes.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=opcoes)
    aba_original = None

    try:
        driver.get(URL_JOGO)
        input("\n>>> Faça o login no jogo e pressione ENTER para iniciar o assistente...\n")

        # Abre e foca na nova aba premium
        aba_original = abrir_e_focar_aba_premium(driver)
        if not aba_original:
            logger.error("Falha na inicialização. Encerrando.")
            return

        # Loop interativo, agora operando exclusivamente na nova aba
        while True:
            saldo_diamantes = obter_saldo_diamantes(driver)
            taxas_atuais, segundos_restantes = obter_dados_da_tela(driver)

            print("\n" + "=" * 50)
            logger.info(f"Saldo de Diamantes: {saldo_diamantes:n}")
            logger.info(f"Tempo para Próxima Atualização: {formatar_segundos(segundos_restantes)}")
            print("-" * 50)
            logger.info("Taxas de Câmbio (por 1 Diamante):")
            for i, recurso in enumerate(RECURSOS):
                taxa = taxas_atuais.get(recurso, 0.0)
                print(f"  [{i + 1}] {recurso}: {int(taxa):n}  (Notação: {taxa:.2e})")
            print("-" * 50)

            # Menu de ações atualizado
            print("Escolha uma ação:")
            print(f"  [{len(RECURSOS) + 1}] Atualizar Taxas (Recarregar Aba)")
            print(f"  [{len(RECURSOS) + 2}] Sair")

            escolha = input(">>> Digite o número da sua escolha: ").strip()

            if not escolha.isdigit():
                print("Entrada inválida. Tente novamente.")
                time.sleep(2)
                continue

            escolha_num = int(escolha)

            if escolha_num == len(RECURSOS) + 2:
                logger.info("Encerrando o assistente...")
                break
            elif escolha_num == len(RECURSOS) + 1:
                logger.info("Recarregando a aba para atualizar as taxas...")
                driver.refresh()
                # Valida o carregamento após o refresh
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, "//img[@title='Dinheiro']"))
                )
                continue
            elif 1 <= escolha_num <= len(RECURSOS):
                recurso_escolhido = RECURSOS[escolha_num - 1]
                quantidade = validar_entrada_numerica(
                    f"Quantidade de diamantes para trocar por {recurso_escolhido} (Máx: {saldo_diamantes:n}): ",
                    minimo=1,
                    maximo=saldo_diamantes
                )
                if quantidade is not None:
                    efetuar_troca_na_tela(driver, recurso_escolhido, quantidade)
                else:
                    logger.info("Operação de troca cancelada.")
                input("\n>>> Pressione ENTER para voltar ao menu...")
            else:
                print("Opção inválida. Tente novamente.")
                time.sleep(2)

    finally:
        logger.info("Fechando o navegador.")
        # Fecha apenas a aba do bot e retorna para a aba original antes de encerrar tudo
        if aba_original and len(driver.window_handles) > 1:
            driver.close()  # Fecha a aba atual (do bot)
            driver.switch_to.window(aba_original)

        driver.quit()


if __name__ == "__main__":
    principal()
