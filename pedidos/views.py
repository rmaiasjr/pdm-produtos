from django.db.models import Prefetch
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from app_produtos.decorators import tratar_erros
from app_produtos.exceptions import NaoEncontrado, IdObrigatorio, MetodoNaoPermitido
from app_produtos.utils import validar_json
from .models import Pedido, ItemPedido
from .utils import serializar_pedido
from .services import (
    validar_pedido, criar_pedido, atualizar_pedido, excluir_pedido, consultar_rentabilidade
)


def _pedidos():
    """Consulta base: carrega cliente, itens e produtos de uma vez (evita N+1)."""
    itens_ativos = ItemPedido.objects.filter(excluido=False).select_related("produto").order_by("id")
    return (
        Pedido.objects.filter(excluido=False)
        .select_related("cliente")
        .prefetch_related(Prefetch("itens", queryset=itens_ativos))
    )

def _buscar_pedido(pedido_id):
    """Retorna o pedido ou levanta NaoEncontrado."""
    pedido = _pedidos().filter(id=pedido_id).first()
    if not pedido:
        raise NaoEncontrado("Pedido")
    return pedido


def _parse_e_validar(request, parcial=False):
    """Faz parse do JSON e valida os dados, levantando ApiError em caso de falha."""
    dados, _ = validar_json(request)
    return validar_pedido(dados, parcial=parcial)


@csrf_exempt
@tratar_erros
def pedidos_view(request, pedido_id=None):

    if request.method == "GET":
        if pedido_id:
            return JsonResponse(serializar_pedido(_buscar_pedido(pedido_id)))
        dados = [serializar_pedido(p) for p in _pedidos().order_by("-id")]
        return JsonResponse(dados, safe=False)

    elif request.method == "POST":
        dados = _parse_e_validar(request)
        id_criado = criar_pedido(dados)
        return JsonResponse({"id": id_criado}, status=201)

    elif request.method == "PUT":
        if not pedido_id:
            raise IdObrigatorio()
        pedido = _buscar_pedido(pedido_id)
        dados = _parse_e_validar(request, parcial=True)
        atualizar_pedido(pedido, dados)
        return JsonResponse({"mensagem": "Atualizado com sucesso"})
    
    elif request.method == "DELETE":
        if not pedido_id:
            raise IdObrigatorio()
        excluir_pedido(_buscar_pedido(pedido_id))
        return JsonResponse({"mensagem": "Excluído com sucesso"})
    
    raise MetodoNaoPermitido()


@csrf_exempt
@tratar_erros
def rentabilidade_view(request):
    if request.method != "GET":
        raise MetodoNaoPermitido()
    resultado = consultar_rentabilidade(
        request.GET.get("produto_id"),
        request.GET.get("preco"),
    )
    return JsonResponse(resultado)