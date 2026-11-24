import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


@pytest.fixture(scope="session")
def base_url():
    return os.getenv(
        "BASE_URL",
        "https://qa.edayinternational.com"
    ).rstrip("/")


@pytest.fixture
def driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    browser = webdriver.Chrome(options=options)
    browser.set_page_load_timeout(30)

    yield browser

    browser.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        browser = item.funcargs.get("driver")

        if browser is not None:
            os.makedirs("artifacts/screenshots", exist_ok=True)

            screenshot = (
                f"artifacts/screenshots/{item.name}.png"
            )

            browser.save_screenshot(screenshot)
            print(f"Failure screenshot: {screenshot}")
