import uuid
import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


def wait_for_message(driver, element_id, expected):
    locator = (By.ID, element_id)

    WebDriverWait(driver, 20).until(
        EC.text_to_be_present_in_element(locator, expected)
    )

    element = driver.find_element(*locator)
    assert "success" in element.get_attribute("class").split()

    return element.text


def require_qa(base_url):
    assert base_url == "https://qa.edayinternational.com", (
        "Write tests are permitted only in QA"
    )


def test_tc01_homepage(driver, base_url):
    driver.get(base_url)

    assert "ShopSphere" in driver.title
    assert driver.find_element(By.ID, "site-title").text == "ShopSphere"


def test_tc02_product_catalog(driver, base_url):
    driver.get(base_url)

    wait_for_message(
        driver, "product-message",
        "Products loaded successfully"
    )

    products = driver.find_elements(
        By.CSS_SELECTOR, "#product-list .product"
    )

    assert len(products) > 0


def test_tc03_refresh_products(driver, base_url):
    driver.get(base_url)

    wait_for_message(
        driver, "product-message",
        "Products loaded successfully"
    )

    old_product = driver.find_element(
        By.CSS_SELECTOR, "#product-list .product"
    )

    driver.find_element(By.ID, "refresh-products").click()

    WebDriverWait(driver, 20).until(
        EC.staleness_of(old_product)
    )

    wait_for_message(
        driver, "product-message",
        "Products loaded successfully"
    )

    products = WebDriverWait(driver, 20).until(
        EC.visibility_of_any_elements_located(
            (By.CSS_SELECTOR, "#product-list .product")
        )
    )

    assert len(products) > 0


def test_tc04_user_registration(driver, base_url):
    require_qa(base_url)
    driver.get(base_url)

    email = f"qa-{uuid.uuid4().hex}@example.com"

    driver.find_element(By.ID, "user-name").send_keys(
        "Selenium QA User"
    )

    driver.find_element(By.ID, "user-email").send_keys(email)
    driver.find_element(By.ID, "register-button").click()

    wait_for_message(
        driver, "registration-result",
        "Registration successful! User ID:"
    )


def test_tc05_tc06_order_and_payment(driver, base_url):
    require_qa(base_url)
    driver.get(base_url)

    wait_for_message(
        driver, "product-message",
        "Products loaded successfully"
    )

    product = Select(
        driver.find_element(By.ID, "product-select")
    )

    assert len(product.options) > 1
    product.select_by_index(1)

    quantity = driver.find_element(By.ID, "order-quantity")
    quantity.clear()
    quantity.send_keys("1")

    driver.find_element(By.ID, "place-order-button").click()

    wait_for_message(
        driver, "order-result",
        "Order created! Order ID:"
    )

    order_id = driver.find_element(
        By.ID, "payment-order-id"
    ).get_attribute("value")

    assert order_id.isdigit()
    assert int(order_id) > 0

    driver.find_element(By.ID, "pay-button").click()

    wait_for_message(
        driver, "payment-result",
        "Mock Payment"
    )


def test_tc07_invalid_email(driver, base_url):
    driver.get(base_url)

    driver.find_element(By.ID, "user-name").send_keys(
        "Invalid QA User"
    )

    email = driver.find_element(By.ID, "user-email")
    email.send_keys("invalid-email")

    assert driver.execute_script(
        "return arguments[0].validity.typeMismatch;",
        email
    ) is True
