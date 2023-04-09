from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response_data = response.data.copy()
        response.data.clear()
        response.data['data'] = response_data

        if response.status_code >= 500:
            response.data['status'] = 'error'
        else:
            response.data['status'] = 'fail'

    return response
