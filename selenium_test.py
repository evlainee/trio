import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app_factory import create_app
from models import InvestorPortfolio, Stock


@pytest.fixture(scope="session")
def driver():
    # Здесь предполагается, что вы используете ChromeDriver
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(20)  # Устанавливаем неявное ожидание
    yield driver
    driver.quit()


def login_selenium(driver, num, password):
    driver.get("http://localhost:5000/auth/login")
    num_field = driver.find_element(By.NAME, "num")
    password_field = driver.find_element(By.NAME, "password")
    num_field.send_keys(num)
    password_field.send_keys(password)
    driver.find_element(By.XPATH, "//button[contains(text(), 'Register')]").click()

def test_portfolio_page_with_login_selenium(driver):
    login_selenium(driver, "79089884917", "12345678")
    driver.get("http://localhost:5000/portfolio")
    assert "Please log in to view this page." not in driver.page_source


def test_buy_stock_selenium(driver):
    # Логин перед выполнением операции покупки
    login_selenium(driver, "79089884917", "12345678")

    # Переход на страницу акции
    driver.get("http://localhost:5000/stock/AFLT")
    time.sleep(5)
    # Нажатие на кнопку "Купить"
    buy_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, "buyButton"))
    )
    buy_button.click()

    # Ожидание появления модального окна и ввод количества
    lot_amount_field = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.ID, "lotAmount"))
    )
    time.sleep(5)
    lot_amount_field.clear()  # Очистка поля перед вводом, на случай если уже есть значение
    lot_amount_field.send_keys("100")
    time.sleep(5)
    # Нажатие на кнопку "Подтвердить" в модальном окне
    confirm_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, "confirmTradeButton"))
    )
    confirm_button.click()


def test_sell_stock_selenium(driver):
    # Логин перед выполнением операции покупки
    login_selenium(driver, "71234567890", "12345678")

    # Переход на страницу акции
    driver.get("http://localhost:5000/stock/EUTR")
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
    time.sleep(5)
    lot_amount_field.clear()  # Очистка поля перед вводом, на случай если уже есть значение
    lot_amount_field.send_keys("10")
    time.sleep(5)
    # Нажатие на кнопку "Подтвердить" в модальном окне
    confirm_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, "confirmTradeButton"))
    )
    confirm_button.click()

