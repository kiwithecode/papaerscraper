import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configurar ChromeDriver
options = webdriver.ChromeOptions()
prefs = {"download.default_directory": "C:/Users/KIWIRAZER/Desktop/ieee_scraper/downloaded_pdfs"}
options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    # Abrir la URL del PDF
    driver.get("https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=9874750")
    
    # Esperar a que el botón de descarga sea visible y hacer clic en él
    download_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//cr-icon-button[@id="download"]'))
    )
    download_button.click()

    # Esperar a que se complete la descarga
    time.sleep(10)  # Ajusta el tiempo de espera según la velocidad de descarga
finally:
    driver.quit()
