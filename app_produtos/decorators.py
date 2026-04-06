from functools import wraps
from django.http import JsonResponse
from .exceptions import ApiError

def tratar_erros(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        try:
            return view_func(*args, **kwargs)
        except ApiError as e:
            return JsonResponse({"erro": e.mensagem}, status=e.status)
        except Exception:
            return JsonResponse({"erro": "Erro interno do servidor"}, status=500)
    return wrapper