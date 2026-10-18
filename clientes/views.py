from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from app_produtos.decorators import tratar_erros
from app_produtos.exceptions import NaoEncontrado, MetodoNaoPermitido

from .models import Cliente
from .utils import serializar_cliente


@csrf_exempt
@tratar_erros
def clientes_view(request, cliente_id=None):
    """Somente leitura: lista os clientes ou retorna um cliente pelo ID."""
    if request.method != "GET":
        raise MetodoNaoPermitido()

    if cliente_id:
        cliente = Cliente.objects.filter(id=cliente_id).first()
        if not cliente:
            raise NaoEncontrado("Cliente")
        return JsonResponse(serializar_cliente(cliente))

    dados = [serializar_cliente(c) for c in Cliente.objects.order_by("nome")]
    return JsonResponse(dados, safe=False)