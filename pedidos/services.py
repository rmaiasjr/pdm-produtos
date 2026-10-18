from decimal import Decimal, InvalidOperation
from django.db import transaction
from app_produtos.exceptions import ApiError
from app_produtos.models import Produto
from clientes.models import Cliente
from .models import Pedido, ItemPedido


RUIM = ItemPedido.NivelRentabilidade.RUIM


# FUNÇÕES AUXILIARES
def _eh_inteiro(valor):
    return isinstance(valor, int) and not isinstance(valor, bool)


def _para_preco(valor):
    """Converte para Decimal e valida: maior que zero e no máximo 2 casas decimais.
    Levanta ValueError com a mensagem de erro em caso de falha."""
    if valor is None or isinstance(valor, bool):
        raise ValueError("Preço inválido")
    try:
        preco = Decimal(str(valor)) 
    except InvalidOperation:
        raise ValueError("Preço inválido")

    if not preco.is_finite():
        raise ValueError("Preço inválido")
    if preco <= 0:
        raise ValueError("Preço deve ser maior que zero")
    if preco != preco.quantize(Decimal("0.01")):
        raise ValueError("Preço deve ter no máximo 2 casas decimais")
    return preco


def _calcular_nivel(produto, preco_liquido):
    """Regra definida no model Pedido."""
    item = ItemPedido(preco_bruto=produto.preco_unitario, preco_liquido=preco_liquido)
    return item.calcular_nivel_rentabilidade()


# VALIDAÇÕES DO PEDIDO
def _validar_item(item, produtos):
    """Valida um item. Retorna (item_limpo, erros)."""
    if not isinstance(item, dict):
        return None, {"item": "Item inválido"}

    erros = {}
    produto = None
    preco = None

    # Produto
    produto_id = item.get("produto_id")
    if not _eh_inteiro(produto_id):
        erros["produto_id"] = "Produto é obrigatório"
    else:
        produto = produtos.get(produto_id)
        if produto is None:
            erros["produto_id"] = "Produto não encontrado"

    # Quantidade (inteiro > 0 e múltiplo de venda)
    quantidade = item.get("quantidade")
    if not _eh_inteiro(quantidade) or quantidade <= 0:
        erros["quantidade"] = "Quantidade deve ser um número inteiro maior que zero"
    elif produto and produto.multiplo and quantidade % produto.multiplo != 0:
        erros["quantidade"] = f"Este produto só pode ser vendido em múltiplos de {produto.multiplo}"

    # Preço do item: se não for informado, assume o preço sugerido (preço do produto)
    preco_informado = item.get("preco_liquido")
    if preco_informado is None:
        if produto:
            preco = produto.preco_unitario
    else:
        try:
            preco = _para_preco(preco_informado)
        except ValueError as e:
            erros["preco_liquido"] = str(e)

    # Rentabilidade 
    nivel = None
    if produto and preco is not None:
        nivel = _calcular_nivel(produto, preco)
        if nivel == RUIM:
            erros["preco_liquido"] = (
                "Rentabilidade ruim: o preço não pode ser mais de 10% menor que o preço do produto"
            )

    if erros:
        return None, erros

    return {
        "produto": produto,
        "quantidade": quantidade,
        "preco_liquido": preco,
        "nivel_rentabilidade": nivel.value,
    }, None


def validar_pedido(dados, parcial=False):
    """Valida o corpo da requisição e retorna os dados já convertidos"""
    if not isinstance(dados, dict):
        raise ApiError("O corpo da requisição deve ser um objeto JSON", status=400)

    if parcial and not ({"cliente_id", "itens"} & dados.keys()):
        raise ApiError("Informe ao menos um campo para atualizar (cliente_id ou itens)", status=400)

    erros = {}
    limpos = {}

    # Cliente
    if not parcial or "cliente_id" in dados:
        cliente_id = dados.get("cliente_id")
        if not _eh_inteiro(cliente_id):
            erros["cliente_id"] = "Cliente é obrigatório"
        else:
            cliente = Cliente.objects.filter(id=cliente_id).first()
            if cliente is None:
                erros["cliente_id"] = "Cliente não encontrado"
            else:
                limpos["cliente"] = cliente

    # Itens
    if not parcial or "itens" in dados:
        itens = dados.get("itens")
        if not isinstance(itens, list) or not itens:
            erros["itens"] = "O pedido deve ter ao menos um item"
        else:
            ids = {i.get("produto_id") for i in itens
                   if isinstance(i, dict) and _eh_inteiro(i.get("produto_id"))}
            # uma única consulta para todos os produtos (ignora os excluídos)
            produtos = {p.id: p for p in Produto.objects.filter(id__in=ids, excluido=False)}

            itens_limpos, erros_itens = [], []
            for posicao, item in enumerate(itens, start=1):
                item_limpo, erros_item = _validar_item(item, produtos)
                if erros_item:
                    erros_itens.append({"posicao": posicao, **erros_item})
                else:
                    itens_limpos.append(item_limpo)

            if erros_itens:
                erros["itens"] = erros_itens
            else:
                limpos["itens"] = itens_limpos

    if erros:
        raise ApiError(erros, status=400)

    return limpos


# DEFINIÇÕES DO CRUD
def _gravar_itens(pedido, itens):
    ItemPedido.objects.bulk_create([
        ItemPedido(
            pedido=pedido,
            produto=i["produto"],
            quantidade=i["quantidade"],
            preco_bruto=i["produto"].preco_unitario,  # preço do produto no momento da venda
            preco_liquido=i["preco_liquido"],
            nivel_rentabilidade=i["nivel_rentabilidade"],
        )
        for i in itens
    ])


@transaction.atomic
def criar_pedido(dados):
    pedido = Pedido.objects.create(cliente=dados["cliente"])
    _gravar_itens(pedido, dados["itens"])
    return pedido.id


@transaction.atomic
def atualizar_pedido(pedido, dados):
    if "cliente" in dados:
        pedido.cliente = dados["cliente"]

    if "itens" in dados:
        # a lista enviada substitui os itens atuais: os antigos ficam marcados como
        # excluídos (histórico preservado) e os novos são criados
        pedido.itens.filter(excluido=False).update(excluido=True)
        _gravar_itens(pedido, dados["itens"])

    pedido.save()  # atualiza ultima_alteracao (auto_now)


@transaction.atomic
def excluir_pedido(pedido):
    # exclusão lógica: o pedido e seus itens ativos ficam marcados como excluídos
    pedido.itens.filter(excluido=False).update(excluido=True)
    pedido.excluido = True
    pedido.save()


# CONSULTA DE RENTABILIDADE (usada pela tela ao escolher o produto / alterar o preço)
def consultar_rentabilidade(produto_id, preco):
    erros = {}

    produto = None
    try:
        produto = Produto.objects.filter(id=int(produto_id), excluido=False).first()
        if produto is None:
            erros["produto_id"] = "Produto não encontrado"
    except (TypeError, ValueError):
        erros["produto_id"] = "Produto é obrigatório"

    try:
        preco_liquido = _para_preco(preco)
    except ValueError as e:
        erros["preco"] = str(e)

    if erros:
        raise ApiError(erros, status=400)

    nivel = _calcular_nivel(produto, preco_liquido)
    return {
        "produto_id": produto.id,
        "preco_bruto": float(produto.preco_unitario),
        "preco_liquido": float(preco_liquido),
        "nivel_rentabilidade": nivel.value,
        "nivel_rentabilidade_label": nivel.label,
        "permitido": nivel != RUIM,
    }