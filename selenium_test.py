import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.fixture(scope="session")
def driver():
    options = webdriver.safari.options.Options()
    driver = webdriver.Safari(options=options)
    driver.implicitly_wait(10)  # Уменьшаем ожидание для ускорения тестов
    yield driver
    driver.quit()

def login_selenium(driver, num, password):
    driver.get("http://localhost:1241/auth/login")
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.NAME, "num"))).send_keys(num)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.XPATH, "//button[contains(text(), 'Войти')]").click()
    WebDriverWait(driver, 10).until(EC.url_contains("portfolio"))  # Ждём успешного входа

def test_portfolio_page_with_login_selenium(driver):
    login_selenium(driver, "79089884917", "12345678")
    driver.get("http://localhost:1241/portfolio")
    assert "Please log in to view this page." not in driver.page_source

def test_buy_stock_selenium(driver):
    # Логин перед выполнением операции покупки
    login_selenium(driver, "79089884917", "12345678")

    # Переход на страницу акции
    driver.get("http://localhost:1241/stock/AFLT")
    time.sleep(3)
    # Нажатие на кнопку "Купить"
    buy_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, "buyButton"))
    )
    buy_button.click()

    # Ожидание появления модального окна и ввод количества
    lot_amount_field = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.ID, "lotAmount"))
    )
    time.sleep(3)
    lot_amount_field.clear()  # Очистка поля перед вводом, на случай если уже есть значение
    lot_amount_field.send_keys("100")
    time.sleep(3)
    # Нажатие на кнопку "Подтвердить" в модальном окне
    confirm_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, "confirmTradeButton"))
    )
    confirm_button.click()
    time.sleep(3)

def test_sell_stock_selenium(driver):
    # Переход на страницу акции
    driver.get("http://localhost:1241/stock/OZON")
    time.sleep(5)
    # Нажатие на кнопку "Купить"
    buy_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, "sellButton"))
    )
    buy_button.click()

    # Ожидание появления модального окна и ввод количества
    lot_amount_field = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.ID, "lotAmount"))
    )
    time.sleep(3)
    lot_amount_field.clear()  # Очистка поля перед вводом, на случай если уже есть значение
    lot_amount_field.send_keys("1")
    time.sleep(3)
    # Нажатие на кнопку "Подтвердить" в модальном окне
    confirm_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, "confirmTradeButton"))
    )
    confirm_button.click()
