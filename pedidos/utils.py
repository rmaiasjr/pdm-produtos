from decimal import Decimal


def serializar_item(item):
    subtotal = item.preco_liquido * item.quantidade
    return {
        "id": item.id,
        "produto_id": item.produto_id,
        "produto_nome": item.produto.nome,
        "produto_codigo": item.produto.codigo,
        "quantidade": item.quantidade,
        "preco_bruto": float(item.preco_bruto),
        "preco_liquido": float(item.preco_liquido),
        "rentabilidade": item.get_nivel_rentabilidade_display(),
        "subtotal": float(subtotal),
    }


def serializar_pedido(pedido):
    itens = [i for i in pedido.itens.all() if not i.excluido]
    total = sum((i.preco_liquido * i.quantidade for i in itens), Decimal("0"))

    return {
        "id": pedido.id,
        "data_emissao": pedido.data_emissao.isoformat(),
        "ultima_alteracao": pedido.ultima_alteracao.isoformat(),
        "cliente": {
            "id": pedido.cliente_id,
            "nome": pedido.cliente.nome,
        },
        "itens": [serializar_item(i) for i in itens],
        "total": float(total),
    }