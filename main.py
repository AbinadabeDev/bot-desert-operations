from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
import time
import logging

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


def ajustar_slider(driver, recurso, quantidade_alvo, delay_clique=0.1):
    """Ajusta o slider para a quantidade alvo. Retorna True se bem-sucedido."""
    try:
        seta_direita = driver.find_element(By.XPATH, XPATHS_RECURSOS[recurso]["increase"])
        seta_esquerda = driver.find_element(By.XPATH, XPATHS_RECURSOS[recurso]["decrease"])

        quantidade_atual = obter_valor_slider(driver, recurso)
        diferenca = quantidade_alvo - quantidade_atual

        if diferenca == 0:
            logger.info(f"Slider já está em {quantidade_alvo}")
            return True

        seta = seta_direita if diferenca > 0 else seta_esquerda
        cliques_necessarios = abs(diferenca)

        logger.info(f"Ajustando slider de {quantidade_atual} para {quantidade_alvo} ({cliques_necessarios} cliques)")

        for i in range(cliques_necessarios):
            seta.click()
            time.sleep(delay_clique)
            if i % 50 == 0 and i > 0:
                logger.info(f"Progresso: {i}/{cliques_necessarios} cliques")

        # Verificar valor final
        time.sleep(0.5)
        valor_final = obter_valor_slider(driver, recurso)

        if valor_final == quantidade_alvo:
            logger.info(f"✅ Slider ajustado corretamente para {quantidade_alvo}")
            return True
        else:
            logger.warning(f"⚠️ Valor final ({valor_final}) difere do alvo ({quantidade_alvo})")
            return False

    except Exception as e:
        logger.error(f"Erro ao ajustar slider: {e}")
        return False


# ============================
# FUNÇÕES PRINCIPAIS
# ============================

def obter_saldo_diamantes(driver):
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

        if saldo_diamantes_str and saldo_diamantes_str.isdigit():
            saldo_diamantes = int(saldo_diamantes_str)
            logger.info(f"💎 Saldo de diamantes encontrado: {saldo_diamantes}")
        else:
            logger.warning("Não foi possível ler o atributo 'max' do slider. Retornando 0.")
            saldo_diamantes = 0

        fechar_lightbox(driver)
        return saldo_diamantes

    except Exception as e:
        logger.error(f"Erro ao obter saldo de diamantes: {e}")
        try:
            fechar_lightbox(driver)
        except:
            pass
        return 0


def obter_tempo_restante_e_taxas(driver):
    """Obtém o tempo restante e as taxas atuais."""
    try:
        if not navegar_para_troca_recursos(driver):
            return TEMPO_PADRAO_ESPERA_SEGUNDOS, {}

        # Obter taxas
        taxas = {}
        for recurso in RECURSOS:
            try:
                elemento_valor = driver.find_element(By.XPATH, XPATHS_RECURSOS[recurso]["rate"])
                valor_do_atributo = elemento_valor.get_attribute("title")
                taxas[recurso] = parse_valor_limpo(valor_do_atributo)

            except NoSuchElementException:
                logger.warning(f"Não foi possível obter taxa para {recurso}")
                taxas[recurso] = 0.0

        logger.info("📊 Taxas atuais por 1 diamante:")
        for rec, taxa in taxas.items():
            logger.info(f"  {rec}: {taxa:.2e}")

        # Tentar obter temporizador
        segundos_restantes = TEMPO_PADRAO_ESPERA_SEGUNDOS
        try:
            botao_grafico = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//*[@id='showAccountValueGraph']"))
            )
            botao_grafico.click()

            elemento_temporizador = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'calculation-countdown')]"))
            )
            segundos_restantes_str = elemento_temporizador.get_attribute('data-countdown')
            if segundos_restantes_str and segundos_restantes_str.isdigit():
                segundos_restantes = int(segundos_restantes_str)
                logger.info(f"⏱️ Tempo restante: {segundos_restantes} segundos")
        except (NoSuchElementException, TimeoutException):
            logger.warning("Não foi possível obter temporizador. Usando tempo padrão.")

        fechar_lightbox(driver)
        return segundos_restantes, taxas

    except Exception as e:
        logger.error(f"Erro ao obter tempo/taxas: {e}")
        try:
            fechar_lightbox(driver)
        except:
            pass
        return TEMPO_PADRAO_ESPERA_SEGUNDOS, {}


def efetuar_troca(driver, recurso, quantidade):
    """Realiza a troca de diamantes por recursos."""
    try:
        logger.info(f"🔄 Iniciando troca: {quantidade} diamantes por {recurso}")

        # Ir para HQ primeiro para resetar estado
        try:
            driver.switch_to.default_content()
            driver.switch_to.frame("game-frame")
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//*[@id='menu_hq']"))
            ).click()
            time.sleep(2)
        except:
            logger.warning("Não foi possível clicar em HQ, continuando...")

        if not navegar_para_troca_recursos(driver):
            logger.error("Falha ao navegar para troca de recursos")
            return False

        # Ajustar slider
        if not ajustar_slider(driver, recurso, int(quantidade)):
            logger.error("Falha ao ajustar slider. Cancelando troca.")
            fechar_lightbox(driver)
            return False

        # Confirmar troca
        botao_troca = driver.find_element(By.XPATH, XPATHS_RECURSOS[recurso]["exchange"])
        botao_troca.click()

        logger.info(f"✅ Troca realizada: {quantidade} diamantes → {recurso}")
        time.sleep(2)

        fechar_lightbox(driver)
        return True

    except Exception as e:
        logger.error(f"Erro ao realizar troca: {e}")
        try:
            fechar_lightbox(driver)
        except:
            pass
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
    logger.info('=' * 50)
    logger.info('🤖 BOT DESERT OPERATIONS - TROCA DE RECURSOS')
    logger.info('=' * 50)

    opcoes = webdriver.ChromeOptions()
    # opcoes.add_argument("--headless")  # Descomente para modo headless
    driver = webdriver.Chrome(options=opcoes)

    try:
        driver.get(URL_JOGO)
        input("\n⏸️  Faça login manualmente e pressione ENTER quando estiver pronto...\n")
        time.sleep(5)

        # Entrar no iframe principal
        try:
            logger.info("Mudando para iframe 'game-frame'...")
            WebDriverWait(driver, 20).until(
                EC.frame_to_be_available_and_switch_to_it((By.ID, "game-frame"))
            )
            logger.info("✅ Contexto mudado para 'game-frame'")
        except TimeoutException:
            logger.error("❌ ERRO CRÍTICO: Não foi possível encontrar iframe 'game-frame'")
            return

        # Loop principal
        while True:
            try:
                logger.info("\n" + "=" * 50)
                logger.info("🔄 Iniciando novo ciclo de monitoramento")
                logger.info("=" * 50)

                # Obter saldo
                saldo_diamantes = obter_saldo_diamantes(driver)
                logger.info(f"💎 Saldo atual: {saldo_diamantes} diamantes")

                # Obter taxas e tempo
                tempo_espera, taxas_atuais = obter_tempo_restante_e_taxas(driver)

                if tempo_espera > 0:
                    logger.info(f"⏱️  Aguardando {tempo_espera + 10}s para próxima atualização...")
                    time.sleep(tempo_espera + 10)

                # Obter taxas atualizadas
                _, taxas_atualizadas = obter_tempo_restante_e_taxas(driver)

                # Perguntar sobre troca
                print("\n" + "=" * 50)
                confirmar = input("💬 Deseja realizar uma troca? (sim/nao): ").strip().lower()

                if confirmar in ['sim', 's', 'yes', 'y']:
                    print(f"\n📦 Recursos disponíveis: {', '.join(RECURSOS)}")
                    recurso = input("Escolha o recurso: ").strip()

                    if recurso not in RECURSOS:
                        logger.warning("❌ Recurso inválido")
                        continue

                    quantidade = validar_entrada_numerica(
                        f"💎 Digite a quantidade de diamantes (1-{saldo_diamantes}): ",
                        minimo=1,
                        maximo=saldo_diamantes
                    )

                    if quantidade is None:
                        logger.info("Troca cancelada")
                        continue

                    if efetuar_troca(driver, recurso, quantidade):
                        logger.info("✅ Troca concluída com sucesso!")
                        saldo_diamantes -= quantidade
                    else:
                        logger.error("❌ Falha na troca")
                else:
                    logger.info("Continuando monitoramento...")

                time.sleep(60)

            except KeyboardInterrupt:
                logger.info("\n⏹️  Interrompido pelo usuário")
                break
            except Exception as e:
                logger.error(f"Erro no loop principal: {e}")
                time.sleep(30)

    finally:
        logger.info("🔴 Encerrando bot...")
        driver.quit()


if __name__ == "__main__":
    principal()