from exceptions.exceptions import BaseEchosignException


class ApiError(BaseEchosignException):
    base_echosign_error = 'Received an error HTTP response code from the Echosign API'
