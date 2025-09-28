import logging
import os
import time
from typing import Optional
import undetected_chromedriver as uc
from selenium.common.exceptions import SessionNotCreatedException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


from app.core import settings, logger



def _atualizar_chrome():
    """Força a atualização do Google Chrome usando o winget (para Windows)."""
    logger.info("Tentando atualizar o Google Chrome via winget...")
    cmd = (
        "winget install --id Google.Chrome.EXE --exact "
        "--silent --accept-source-agreements --accept-package-agreements"
    )
    retorno = os.system(cmd)
    if retorno == 0:
        logger.info("Google Chrome atualizado/reinstalado com sucesso!")
    else:
        logger.warning(f"Falha ao atualizar o Google Chrome (código de saída: {retorno})")



def solve_hcaptcha_sync(max_attempts: int = 3) -> Optional[str]:
    """
    Função SÍNCRONA e BLOQUEANTE que executa a lógica do Selenium.
    Esta função será executada em um thread separado para não bloquear a API.
    """
    driver: Optional[uc.Chrome] = None
    for attempt in range(1, max_attempts + 1):
        logger.info(f"Tentativa {attempt} de {max_attempts} para resolver o hCaptcha...")

        options = uc.ChromeOptions()
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--incognito")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--headless=new")
        options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
        )
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--profile-directory=Default")
        options.add_argument("--disable-plugins-discovery")
        options.add_argument("--start-maximized")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--allow-running-insecure-content")
        options.accept_insecure_certs = True


        try:
            driver = uc.Chrome(options=options)
            driver.get(settings.hcaptcha_url)

            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-hcaptcha-widget-id]"))
            )
            logger.info("hCaptcha carregado com sucesso.")

            widget_id_element = driver.find_element(By.CSS_SELECTOR, '[data-hcaptcha-widget-id]')
            widget_id = widget_id_element.get_attribute('data-hcaptcha-widget-id')
            logger.info(f"Widget ID encontrado: {widget_id}")

            driver.execute_script(f"hcaptcha.execute('{widget_id}');")
            logger.info("Script hcaptcha.execute() injetado.")


            token = WebDriverWait(driver, 25).until(
                lambda d: d.execute_script(f"return hcaptcha.getResponse('{widget_id}');")
            )

            if token:
                logger.info("Token hCaptcha obtido com sucesso.")
                return token
            else:
                logger.warning("Token recebido está vazio. Tentando novamente.")
                continue

        except SessionNotCreatedException as e:
            logger.error(f"Erro ao criar a sessão do driver: {e}")
            logger.info("Tentando atualizar o Google Chrome e reiniciar...")
            _atualizar_chrome()

        except TimeoutException:
            logger.error(f"Erro na tentativa {attempt}: Tempo esgotado ao esperar por um elemento do hCaptcha.")

        except Exception as e:
            logger.error(f"Ocorreu um erro inesperado na tentativa {attempt}: {e}", exc_info=True)

        finally:
            if driver:
                driver.quit()
            # Garante que os processos sejam limpos, mesmo em caso de erro.
            #_kill_chrome_processes(driver)

        if attempt < max_attempts:
            logger.info("Aguardando 2 segundos antes da próxima tentativa...")
            time.sleep(2)

    logger.error("Todas as tentativas de resolver o hCaptcha falharam.")
    return None
