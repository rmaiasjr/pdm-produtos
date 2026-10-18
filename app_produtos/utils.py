import json
from .exceptions import ApiError


def validar_json(request):
    try:
        body = json.loads(request.body)
        return body, None
    except (json.JSONDecodeError, ValueError):
        raise ApiError("JSON inválido", status=400)
    

def serializar_produto(produto, request=None):
    imagem = None
    if produto.imagem:
        # Se tiver o request, gera URL absoluta; senão, retorna o path relativo
        imagem = request.build_absolute_uri(produto.imagem.url) if request else produto.imagem.url

    
    return {
        "id": produto.id,
        "nome": produto.nome,
        "codigo": produto.codigo,
        "preco_unitario": float(produto.preco_unitario),
        "multiplo": int(produto.multiplo),
        "ultma_alteracao": produto.ultma_alteracao.isoformat(),
        "imagem": imagem
    }