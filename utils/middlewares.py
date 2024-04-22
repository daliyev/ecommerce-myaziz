import traceback

import requests


class SendErrorToBotMiddleware:
    def __init__(self, get_response, model=None):
        self.get_response = get_response
        self.model = model

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):

        token = "7061215872:AAE9FzKlpOiP0fekIrvyyoUEvJqdAOQKC6E"
        chat_id = "6050173548"
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        traceback_info = traceback.format_exc()
        exception_type = type(exception).__name__
        message = f"Ecommerce\n{exception_type}: {str(exception)}\n\n{traceback_info}\n\nEcommerce"
        data = {
            'chat_id': chat_id,
            'text': message
        }
        requests.post(url=url, params=data)
