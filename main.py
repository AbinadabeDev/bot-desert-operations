from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
import time
import logging
import locale

# ============================
# CONFIGURAÇÕES
# ============================
URL_JOGO = "https://desertoperations.fawkesgames.com/"
TEMPO_PADRAO_ESPERA_SEGUNDOS = 60
RECURSOS = ["Dinheiro", "Ouro", "Munição", "Diesel", "Querosene"]

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# ============================
# XPATHS DOS RECURSOS
# ============================
XPATHS_RECURSOS = {}
for recurso in RECURSOS:
    # Este bloco localiza o container geral de cada recurso
    bloco_recurso = f"//div[contains(@class, 'premiumResourceGridItem') and .//img[@title='{recurso}']]"

    XPATHS_RECURSOS[recurso] = {
        # Procura a taxa DENTRO do span correto
        "rate": f"{bloco_recurso}//span[contains(@class, 'tooltipExtention')]",

        "quantity": f"{bloco_recurso}//span[starts-with(@id, 'sliderCountDiaExchange')]",
        "increase": f"{bloco_recurso}//span[contains(@class, 'sliderAmountExchangeIcon') and contains(@class, 'right')]",
        "decrease": f"{bloco_recurso}//span[contains(@class, 'sliderAmountExchangeIcon') and contains(@class, 'left')]",
        "exchange": f"{bloco_recurso}//a[contains(@class, 'getPremiumResources')]",
    }


# ============================
# FUNÇÕES AUXILIARES
# ============================

def parse_valor_limpo(valor_str):
    """Converte uma string de número limpa (ex: '10602111...') para float."""
    try:
        # Remove pontos que são usados como separador de milhar
        valor_limpo = valor_str.replace('.', '')
        return float(valor_limpo)
    except Exception as e:
        logger.error(f"Erro ao parsear valor limpo: {valor_str} - {e}")
        return 0.0

        # Fallback: valor simples
        return float(valor_str)
    except Exception as e:
        logger.error(f"Erro ao parsear valor: {valor_str} - {e}")
        return 0.0


def aguardar_elemento_com_retry(driver, by, value, timeout=10, max_retries=3):
    """Aguarda elemento com retry em caso de StaleElementReference."""
    for tentativa in range(max_retries):
        try:
            elemento = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return elemento
        except StaleElementReferenceException:
            if tentativa == max_retries - 1:
                raise
            time.sleep(0.5)
    return None


def fechar_lightbox(driver):
    """Fecha a lightbox e retorna ao contexto do jogo (game-frame)."""
    try:
        # Para sair do 'lightBoxFrame' e voltar para o 'game-frame', usamos parent_frame()
        logger.info("Retornando para o frame principal do jogo ('game-frame')...")
        driver.switch_to.parent_frame()

        # Agora que estamos no 'game-frame', podemos procurar o botão de fechar.
        # Muitas vezes, o botão de fechar está no frame pai.
        try:
            # O ID que você forneceu no HTML é 'lightBoxClose'
            botao_fechar = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "lightBoxClose"))
            )
            botao_fechar.click()
            logger.info("Lightbox fechada (pelo ID 'lightBoxClose')")
        except TimeoutException:
            logger.warning("Não encontrou o botão de fechar. A lightbox pode ter fechado sozinha.")

        # Apenas para garantir que o contexto final é o 'game-frame'
        logger.info("✅ Contexto retornado para 'game-frame'")
        time.sleep(1) # Pequena pausa para a UI atualizar

    except Exception as e:
        logger.error(f"Erro ao fechar lightbox: {e}")
        # Em caso de erro, tentamos forçar o retorno ao game-frame
        try:
            driver.switch_to.default_content()
            driver.switch_to.frame("game-frame")
        except:
            logger.error("Falha crítica ao tentar retornar ao 'game-frame'")


def atualizar_cambio_via_hq(driver):
    """Fecha a janela de troca, clica em HQ para atualizar e reabre a janela de troca."""
    try:
        logger.info("🚀 Iniciando atualização completa das taxas de câmbio via HQ...")

        # ETAPA 1: Fecha a janela de troca atual
        logger.info("Fechando a janela de troca...")
        fechar_lightbox(driver)  # Isso nos devolve ao 'game-frame'

        # ETAPA 2: Clica no botão HQ no menu principal
        logger.info("Navegando para o Quartel-General (HQ) para forçar a atualização...")
        hq_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.ID, "menu_hq"))
        )
        hq_button.click()

        # Pequena pausa para garantir que a atualização do estado do jogo seja processada
        time.sleep(2)
        logger.info("Refresh via HQ concluído.")

        # ETAPA 3: Reabre a janela de troca de recursos
        logger.info("Retornando para a tela de troca de recursos...")
        if not navegar_para_troca_recursos(driver):
            logger.error("Falha ao retornar para a tela de troca após atualização.")
            return False

        logger.info("✅ Atualização completa concluída. Novas taxas carregadas.")
        return True

    except Exception as e:
        logger.error(f"Ocorreu um erro durante a atualização via HQ: {e}")
        return False


def navegar_para_troca_recursos(driver):
    """Navega para Premium > Troca de Recursos (com iframes aninhados). Retorna True se bem-sucedido."""
    try:
        # 1. Garantir que estamos no 'game-frame'
        logger.info("Garantindo contexto do 'game-frame'...")
        driver.switch_to.default_content()
        WebDriverWait(driver, 15).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, "game-frame"))
        )

        # 2. Clicar no botão Premium (já estamos no game-frame)
        logger.info("Clicando no botão 'Premium'...")
        botao_premium = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.ID, "menu_premium"))
        )
        driver.execute_script("arguments[0].click();", botao_premium)

        # 3. AGORA, A MUDANÇA CRÍTICA:
        # O lightbox está DENTRO do game-frame. NÃO saímos para o default_content.
        # Vamos direto para o iframe filho 'lightBoxFrame'.
        logger.info("Aguardando o iframe aninhado 'lightBoxFrame'...")
        WebDriverWait(driver, 20).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, "lightBoxFrame"))
        )
        logger.info("✅ Entrou no iframe aninhado 'lightBoxFrame'")

        # 4. Esperar e clicar no botão "Troca de Recursos"
        logger.info("Procurando botão 'Troca de Recursos' dentro do iframe aninhado...")
        resource_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='premium_cash.php?section=ress']"))
        )
        driver.execute_script("arguments[0].click();", resource_button)
        logger.info("✅ Botão 'Troca de Recursos' clicado com sucesso!")

        # 5. Esperar a tela de troca carregar
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//img[@title='Dinheiro']"))
        )
        logger.info("✅ Tela de troca de recursos carregada.")

        return True

    except TimeoutException as e:
        logger.error(f"Timeout ao navegar para troca de recursos: {e}")
        return False
    except Exception as e:
        logger.error(f"Erro inesperado ao navegar para troca de recursos: {e}")
        return False


def obter_valor_slider(driver, recurso, max_retries=3):
    """Obtém o valor atual do slider com retry."""
    for _ in range(max_retries):
        try:
            elemento = driver.find_element(By.XPATH, XPATHS_RECURSOS[recurso]["quantity"])
            return int(elemento.text.strip())
        except (StaleElementReferenceException, ValueError):
            time.sleep(0.2)
    raise Exception(f"Não foi possível obter valor do slider para {recurso}")


def formatar_segundos(total_segundos):
    """Converte um total de segundos para o formato HH:MM:SS."""
    if total_segundos < 0:
        return "00:00:00"
    horas, rem = divmod(total_segundos, 3600)
    minutos, segundos = divmod(rem, 60)
    return f"{int(horas):02d}:{int(minutos):02d}:{int(segundos):02d}"


def ajustar_slider(driver, recurso, quantidade_alvo):
    """Ajusta o slider para a quantidade alvo usando as setas do teclado."""
    try:
        # Mapeia o nome do recurso para o ID do slider
        recurso_id_map = {
            "Dinheiro": "Money", "Ouro": "Gold", "Munição": "Ammunition",
            "Diesel": "Diesel", "Querosene": "Cerosin"
        }
        recurso_suffix = recurso_id_map[recurso]
        slider_id = f"playzoSliderDiaExchange{recurso_suffix}"
        span_id = f"sliderCountDiaExchange{recurso_suffix}"

        # Localiza o pino do slider (o elemento que recebe o foco do teclado)
        slider_handle = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f"#{slider_id} .playzo-slider-button"))
        )

        # Pega o valor atual do slider lendo o span
        valor_atual_str = driver.find_element(By.ID, span_id).text
        quantidade_atual = int(valor_atual_str.replace('.', ''))

        diferenca = quantidade_alvo - quantidade_atual

        if diferenca == 0:
            logger.info(f"Slider de {recurso} já está em {quantidade_alvo}.")
            return True

        logger.info(f"Ajustando slider de {recurso} de {quantidade_atual} para {quantidade_alvo} (usando teclado)...")

        # Escolhe a tecla a ser pressionada
        tecla = Keys.ARROW_RIGHT if diferenca > 0 else Keys.ARROW_LEFT

        # Envia a tecla o número de vezes necessário de forma eficiente
        slider_handle.send_keys(tecla * abs(diferenca))

        # Validação final
        time.sleep(0.5)  # Pequena espera para a UI atualizar
        valor_final_str = driver.find_element(By.ID, span_id).text
        if int(valor_final_str) == quantidade_alvo:
            logger.info("✅ Slider ajustado com sucesso!")
            return True
        else:
            logger.warning(
                f"⚠️ O valor do slider ({valor_final_str}) não corresponde ao alvo ({quantidade_alvo}). A interface pode estar lenta.")
            return False

    except Exception as e:
        logger.error(f"Erro ao ajustar slider com teclado: {e}")
        return False


# ============================
# FUNÇÕES PRINCIPAIS
# ============================

def obter_saldo_diamantes(driver, fechar_ao_final=True):
    """Obtém o saldo de diamantes de forma eficiente, lendo o atributo 'max' do slider."""
    try:
        logger.info("Obtendo saldo de diamantes (método eficiente)...")
        if not navegar_para_troca_recursos(driver):
            return 0

        # Espera o slider do Dinheiro (poderia ser qualquer um) estar presente na tela
        slider_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "playzoSliderDiaExchangeMoney"))
        )
        # Pega o valor do atributo 'max', que é o total de diamantes
        saldo_diamantes_str = slider_container.get_attribute("max")
        saldo_diamantes = int(saldo_diamantes_str) if saldo_diamantes_str and saldo_diamantes_str.isdigit() else 0

        if fechar_ao_final:
            fechar_lightbox(driver)
        return saldo_diamantes
    except Exception as e:
        logger.error(f"Erro ao obter saldo de diamantes: {e}")
        if fechar_ao_final:
            try:
                fechar_lightbox(driver)
            except:
                pass
        return 0


def obter_dados_da_tela(driver):
    """Obtém as taxas e o tempo da tela de troca ATUAL, gerenciando o estado do painel do timer."""
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
        # Verifica se o painel do gráfico já está visível
        graph_panel = driver.find_element(By.ID, "premiumGraph")
        if not graph_panel.is_displayed():
            logger.info("Painel de informações não está visível. Abrindo...")
            botao_grafico = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "showAccountValueGraph")))
            driver.execute_script("arguments[0].click();", botao_grafico)
            WebDriverWait(driver, 5).until(EC.visibility_of(graph_panel))  # Espera o painel aparecer

        # Agora que o painel está garantidamente visível, lemos o timer
        elemento_temporizador = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'calculation-countdown')]")))
        WebDriverWait(driver, 10).until(lambda d: elemento_temporizador.text.strip() != "-")

        future_timestamp = int(elemento_temporizador.get_attribute('data-countdown'))
        current_timestamp = int(time.time())
        segundos_restantes = future_timestamp - current_timestamp
    except Exception:
        logger.warning("Não foi possível obter o timer na atualização.")

    return taxas, segundos_restantes


def efetuar_troca_na_tela(driver, recurso, quantidade):
    """Realiza a troca na tela atual, incluindo a confirmação e o fechamento da caixa de sucesso."""
    try:
        logger.info(f"🔄 Iniciando troca: {quantidade} diamantes por {recurso}")

        if not ajustar_slider(driver, recurso, int(quantidade)):
            logger.error("Falha ao ajustar slider.")
            return False

        botao_troca = driver.find_element(By.XPATH, XPATHS_RECURSOS[recurso]["exchange"])
        botao_troca.click()

        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "messageBoxOverlay")))
        logger.info("Caixa de diálogo de confirmação detectada.")

        while True:
            confirmacao = input("👉 Confirmar troca? [1] Sim, [0 ou 00] Não: ").strip()
            if confirmacao == '1':
                logger.info("Confirmando a troca...")
                ok_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "messageBoxLeftButton")))
                ok_button.click()

                # ETAPA 5: Aguarda a caixa de SUCESSO e clica em "Fechar"
                logger.info("Aguardando confirmação de sucesso...")
                fechar_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "#messageBoxAlertButton .button"))
                )
                logger.info("✅ TROCA FOI BEM-SUCEDIDA!")
                fechar_button.click()

                resultado_final = True
                break
            elif confirmacao in ['0', '00']:
                logger.info("Cancelando a troca...")
                cancel_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "messageBoxRightButton")))
                cancel_button.click()
                resultado_final = False
                break
            else:
                print("❌ Opção inválida. Por favor, digite 1 para Sim ou 0 para Não.")

        # ETAPA 6: Aguarda a caixa de diálogo geral desaparecer
        WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.ID, "messageBoxOverlay")))

        return resultado_final

    except Exception as e:
        logger.error(f"Erro ao realizar troca: {e}")
        return False


def validar_entrada_numerica(prompt, minimo=1, maximo=None):
    """Valida entrada numérica do usuário."""
    while True:
        try:
            valor = input(prompt).strip()
            if valor.lower() in ['sair', 'cancelar', 'nao', 'não']:
                return None

            valor_int = int(valor)

            if valor_int < minimo:
                print(f"❌ Valor deve ser no mínimo {minimo}")
                continue

            if maximo and valor_int > maximo:
                print(f"❌ Valor deve ser no máximo {maximo}")
                continue

            return valor_int
        except ValueError:
            print("❌ Digite um número válido")


# ============================
# FUNÇÃO PRINCIPAL
# ============================

def principal():
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    except locale.Error:
        logger.warning("Locale 'pt_BR.UTF-8' não encontrado. Usando formatação padrão.")

    logger.info('=' * 50)
    logger.info('🤖 BOT DESERT OPERATIONS - ASSISTENTE DE TROCAS')
    logger.info('=' * 50)

    opcoes = webdriver.ChromeOptions()
    opcoes.add_argument('--log-level=3')
    opcoes.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=opcoes)

    try:
        driver.get(URL_JOGO)
        input("\n⏸️  Faça login manualmente e pressione ENTER quando estiver na tela do jogo...\n")

        saldo_diamantes = obter_saldo_diamantes(driver, fechar_ao_final=False)
        if saldo_diamantes == 0:
            logger.error("Não foi possível obter o saldo de diamantes. Encerrando.")
            return

        while True:
            taxas_atuais, segundos_restantes = obter_dados_da_tela(driver)

            print("\n" + "=" * 50)
            logger.info(f"💎 Saldo de Diamantes: {saldo_diamantes:n}")
            logger.info(f"⏱️  Tempo para atualização: {formatar_segundos(segundos_restantes)}")
            print("-" * 50)
            logger.info("📊 Taxas Atuais por 1 Diamante:")
            for i, recurso in enumerate(RECURSOS):
                taxa = taxas_atuais.get(recurso, 0.0)
                print(f"  [{i + 1}] {recurso}: {int(taxa):n}  (Notação: {taxa:.2e})")
            print("-" * 50)

            # MENU ATUALIZADO
            print("Escolha uma opção:")
            print(f"  [{len(RECURSOS) + 1}] Atualizar Dados da Tela (Rápido)")
            print(f"  [{len(RECURSOS) + 2}] ATUALIZAR CÂMBIO VIA HQ (Completo)")
            print(f"  [{len(RECURSOS) + 3}] Sair")

            escolha = input("👉 Digite o número da sua escolha: ").strip()

            if not escolha.isdigit():
                print("❌ Opção inválida. Por favor, digite um número.")
                time.sleep(2)
                continue

            escolha_num = int(escolha)

            # Opção de SAIR
            if escolha_num == len(RECURSOS) + 3:
                logger.info("Saindo...")
                break

            # Opção de ATUALIZAR CÂMBIO VIA HQ
            elif escolha_num == len(RECURSOS) + 2:
                atualizar_cambio_via_hq(driver)
                # O loop continuará e coletará/exibirá os novos dados automaticamente
                continue

            # Opção de ATUALIZAR DADOS (Rápido)
            elif escolha_num == len(RECURSOS) + 1:
                logger.info("Atualizando dados da tela...")
                continue

            # Opções de TROCA
            elif 1 <= escolha_num <= len(RECURSOS):
                recurso_escolhido = RECURSOS[escolha_num - 1]

                quantidade = validar_entrada_numerica(
                    f"💎 Digite a quantidade de diamantes para trocar por {recurso_escolhido} (1-{saldo_diamantes}): ",
                    minimo=1,
                    maximo=saldo_diamantes
                )

                if quantidade is not None:
                    if efetuar_troca_na_tela(driver, recurso_escolhido, quantidade):
                        saldo_diamantes -= quantidade
                    # O log de sucesso/falha já está na outra função
                else:
                    logger.info("Troca cancelada.")

                input("\nPressione ENTER para voltar ao menu...")

            else:
                print("❌ Opção inválida.")
                time.sleep(2)

    finally:
        logger.info("🔴 Encerrando bot...")
        try:
            fechar_lightbox(driver)
        except Exception:
            pass
        driver.quit()


if __name__ == "__main__":
    principal()