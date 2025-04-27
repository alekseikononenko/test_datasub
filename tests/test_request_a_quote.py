import pytest
from playwright.sync_api import sync_playwright
from tests.pages.home_page import RequestAQuotePage

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, slow_mo=0, timeout=5000)
        yield browser
        browser.close()
        p.stop()

@pytest.fixture
def browser_context(browser):
    context = browser.new_context()
    yield context
    context.close()

@pytest.fixture
def page(browser_context):
    page = browser_context.new_page()
    yield page

@pytest.fixture
def request_a_quote_page(page):
    return RequestAQuotePage(page)

def test_request_a_quote_happy_path(request_a_quote_page):
    print("[START] Проверка отправки формы с заполнением полей")
    request_a_quote_page.open()
    request_a_quote_page.fill_form_valid(
        name="John Doe",
        email="john@testmailfdfd.com",
        service="Select C Service",
        purpose="Personal",
        withdrawal=["Cash"],
        message="Hello, I would like a quote."
    )
    request_a_quote_page.check_validation_marks()
    print("[INFO] Отправляем форму, проверяем отправленный запрос и ответ...")
    request_a_quote_page.check_api_request_and_response()
    print("[INFO] Проверка успешного сообщения...")
    assert request_a_quote_page.page.locator("#formStatus").is_visible(), "Сообщение об успешной отправке не найдено"

def test_request_a_quote_negative_empty_fields(request_a_quote_page):
    print("[START] Проверка отправки формы без заполнения обязательных полей (negative case)")
    request_a_quote_page.open()
    request_a_quote_page.fill_form_empty()
    request_a_quote_page.submit_form()
    print("[INFO] Форма отправлена без заполнения, проверка ошибок валидации...")
    assert request_a_quote_page.page.locator("input#name.is-invalid").is_visible(), "Поле Name не подсвечено как обязательное"
    assert request_a_quote_page.page.locator("input#email.is-invalid").is_visible(), "Поле Email не подсвечено как обязательное"
    assert request_a_quote_page.page.locator("select#service.is-invalid").is_visible(), "Поле Service не подсвечено как обязательное"
    assert request_a_quote_page.page.locator("textarea#message.is-invalid").is_visible(), "Поле Message не подсвечено как обязательное"