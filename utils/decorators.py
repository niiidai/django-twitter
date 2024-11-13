from rest_framework.response import Response
from rest_framework import status
from functools import wraps


def required_params(method='GET', params=None):
    """
    The required_params function will wrap the view function in views.py and
    return a decorator after we call @required_params(params=['some_param']).
    """
    if params is None:
        params = []

    def decorator(view_func):
        """
        Here, the decorator send the parameters of the view function
        to _wrapped_view via wraps.
        The instance parameter is self in view_func.
        """
        @wraps(view_func)
        def _wrapped_view(instance, request, *args, **kwargs):
            if method.lower() == 'get':
                data = request.query_params
            else:
                data = request.data
            ## getattr can get both data and queries
            #data = getattr(request, request_attr)
            missing_params = [
                param
                for param in params
                if param not in data
            ]
            if missing_params:
                params_str = ','.join(missing_params)
                return Response({
                    'message': 'missing {} in request'.format(params_str),
                    'success': False,
                }, status=status.HTTP_400_BAD_REQUEST)
            # view_func (wrapped by @required_params) will be called after
            # these validations
            return view_func(instance, request, *args, **kwargs)
        return _wrapped_view
    return decorator