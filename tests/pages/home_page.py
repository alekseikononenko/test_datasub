class RequestAQuotePage:
    def __init__(self, page):
        self.page = page
        self.url = "https://qatest.datasub.com/"
        self.name_input = 'input#name'
        self.email_input = 'input#email'
        self.service_select = 'select#service'
        self.business_radio = 'input#purposeBusiness'
        self.cash_checkbox = 'input#withdrawCash'
        self.message_textarea = 'textarea#message'
        self.submit_button = 'button[type="submit"]'

    def open(self):
        self.page.goto(self.url, wait_until="load")
        self.page.wait_for_selector('body')
        self.page.locator(self.name_input).scroll_into_view_if_needed()
        self.page.wait_for_selector(self.name_input)

    def fill_form_valid(self,
                        name="John Doe",
                        email="john@example.com",
                        service="A Service",
                        purpose="Business",
                        withdrawal=None,
                        message="Hello, I would like a quote."):
        if withdrawal is None:
            withdrawal = ["Cash"]

        self.page.fill(self.name_input, name)
        self.page.fill(self.email_input, email)
        self.page.select_option(self.service_select, label=service)
        if purpose == "Business":
            self.page.check('input#purposeBusiness')
        elif purpose == "Personal":
            self.page.check('input#purposePersonal')
        for option in withdrawal:
            if option == "Cash":
                self.page.check('input#withdrawCash')
            elif option == "Card":
                self.page.check('input#withdrawCard')
            elif option == "Cryptocurrency":
                self.page.check('input#withdrawCrypto')
        self.page.fill(self.message_textarea, message)

    def submit_form(self):
        self.page.click(self.submit_button)

    def fill_form_empty(self):
        # Ничего не заполнять, только нажать сабмит
        pass

    def check_validation_marks(self):
        assert 'is-valid' in self.page.get_attribute(self.name_input, 'class'), "Галочка у поля 'Name' не появилась"
        assert 'is-valid' in self.page.get_attribute(self.email_input, 'class'), "Галочка у поля 'Email' не появилась"
        assert 'is-valid' in self.page.get_attribute(self.service_select, 'class'), "Галочка у поля 'Service' не появилась"
        assert 'is-valid' in self.page.get_attribute(self.message_textarea, 'class'), "Галочка у поля 'Message' не появилась"

    def check_api_request_and_response(self):
        requests_captured = []
        responses_captured = []
        console_errors = []

        def handle_request(request):
            if "api/subscribe" in request.url and request.method == "POST":
                print(f"[INFO] Пойман POST-запрос: {request.method} {request.url}")
                requests_captured.append(request)

        def handle_response(response):
            if "api/subscribe" in response.url and response.request.method == "POST":
                print(f"[INFO] Пойман ответ на POST-запрос: статус {response.status}")
                responses_captured.append(response)

        def handle_console(msg):
            if msg.type == "error":
                console_errors.append(msg.text)

        self.page.on("request", handle_request)
        self.page.on("response", handle_response)
        self.page.on("console", handle_console)

        self.submit_form()
        self.page.wait_for_timeout(1000)

        assert len(requests_captured) == 1, f"Ожидался 1 POST запрос, но поймано {len(requests_captured)}"
        assert len(responses_captured) == 1, f"Ожидался 1 ответ на POST запрос, но поймано {len(responses_captured)}"
        assert responses_captured[0].status < 400, f"Ожидался успешный ответ (<400), но был {responses_captured[0].status}"

        cors_errors = [err for err in console_errors if "CORS" in err or "Access-Control" in err]
        assert not cors_errors, f"Найдены CORS ошибки в консоли браузера: {cors_errors}"