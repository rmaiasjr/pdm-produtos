from django.http import JsonResponse
from .models import ChaveAPI

class MiddlewareChaveAPI:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # Ignorar rotas públicas
        rotas_publicas = ['/admin/', '/login/', '/media/', '/static/']
        if any(request.path.startswith(r) for r in rotas_publicas):
            return self.get_response(request)

        chave = request.headers.get('chave')

        if not chave:
            return JsonResponse({'erro': 'API Key não fornecida'}, status=401)

        try:
            chave_api = ChaveAPI.objects.get(chave=chave)
        except ChaveAPI.DoesNotExist:
            return JsonResponse({'erro': 'API Key inválida'}, status=403)

        if not chave_api.validar():
            return JsonResponse({'erro': 'API Key expirada ou inativa'}, status=403)

        return self.get_response(request)