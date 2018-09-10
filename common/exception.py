# coding=utf-8

import json

from django import http
from django.db import IntegrityError
from rest_framework import exceptions

from common.response import APIResponse
from . import errors


def get_message(data):
    if isinstance(data, list):
        ret = [
            get_message(item) for item in data
        ]
        return ','.join(ret)
    elif isinstance(data, dict):
        ret = [
            '{}{}'.format(key, get_message(value)) for key, value in data.items()
        ]
        return ','.join(ret)
    return data


def exception_handler(exc, context):
    # Authentication
    if isinstance(exc, exceptions.AuthenticationFailed):
        return APIResponse(code=errors.TOKEN_EXPIRED, message=exc.default_detail, data={'detail': exc.detail},
                           status_code=exc.status_code)
    # Throttled
    if isinstance(exc, exceptions.Throttled):
        return APIResponse(code=errors.THROTTLE_REACHED, message=exc.default_detail, data={'detail': exc.detail})

    if isinstance(exc, exceptions.ValidationError):
        return APIResponse(code=errors.PARAMS_ERROR, message=exc.default_code, data={'detail': get_message(exc.detail)})

    if isinstance(exc, Exception):
        return APIResponse(code=errors.OTHER_ERROR, message="服务器错误", data={'detail': str(exc)})

    # Common
    if isinstance(exc, exceptions.APIException):
        # print(exc)
        return APIResponse(code=errors.OTHER_ERROR, message=exc.default_detail, data={'detail': exc.detail})


def server_error(request, template_name=None):
    ret = {
        'code': errors.SYSTEM_ERROR,
        'message': 'server error',
        'data': None
    }
    return http.HttpResponseServerError(json.dumps(ret), content_type='application/json')


def not_found_error(request, template_name=None):
    ret = {
        'code': errors.NOT_FOUND,
        'message': 'not found',
        'data': None
    }
    return http.HttpResponse(json.dumps(ret), content_type='application/json', status=404)
