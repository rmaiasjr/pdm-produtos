from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Produto
from .utils import validar_json, serializar_produto
from .services import validar_produto, criar_produto, atualizar_produto, excluir_produto
from .decorators import tratar_erros
from .exceptions import NaoEncontrado, IdObrigatorio, MetodoNaoPermitido

def _buscar_produto_ativo(produto_id):
    """Retorna o produto ou levanta NaoEncontrado."""
    produto = Produto.objects.filter(id=produto_id, excluido=False).first()
    if not produto:
        raise NaoEncontrado("Produto")
    return produto


def _parse_e_validar(request, parcial=False):
    """Faz parse do JSON e valida os dados, levantando ApiError em caso de falha."""
    dados, erro = validar_json(request)
    if erro:
        raise erro  
    erros = validar_produto(dados, parcial=parcial)
    if erros:
        raise erros 
    return dados

@csrf_exempt
@tratar_erros
def produtos_view(request, produto_id=None):

    if request.method == "GET":
        if produto_id:
            return JsonResponse(serializar_produto(_buscar_produto_ativo(produto_id), request))
        dados = [serializar_produto(p, request) for p in Produto.objects.filter(excluido=False)]
        return JsonResponse(dados, safe=False)

    elif request.method == "POST":
        dados = _parse_e_validar(request)
        id_criado = criar_produto(dados)
        return JsonResponse({"id": id_criado}, status=201)

    elif request.method == "PATCH":
        if not produto_id:
            raise IdObrigatorio()
        dados = _parse_e_validar(request, parcial=True)
        atualizar_produto(_buscar_produto_ativo(produto_id), dados)
        return JsonResponse({"mensagem": "Atualizado com sucesso"})

    elif request.method == "DELETE":
        if not produto_id:
            raise IdObrigatorio()
        excluir_produto(_buscar_produto_ativo(produto_id))
        return JsonResponse({"mensagem": "Excluído com sucesso"})

    raise MetodoNaoPermitido()