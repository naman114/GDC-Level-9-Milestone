from datetime import datetime


class CustomMiddleware(object):
    def __init__(self, get_response):
        # One time configuration and initialisation of the object (with get_response)
        # get_response is the next middleware inline to be executed
        self.get_response = get_response

    def __call__(self, request):
        # Executed for each request before the view and later middleware are called

        # print("Middleware request: ", request)
        # Can now access current_time in templates
        request.current_time = datetime.now()
        response = self.get_response(request)
        return response
