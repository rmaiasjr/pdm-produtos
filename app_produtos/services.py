from decimal import Decimal, InvalidOperation
import os
import requests
from io import BytesIO
from urllib.parse import urlparse
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone
from .models import Produto
from .exceptions import ApiError


# TRATAR IMAGEM
def _baixar_e_salvar_imagem(produto, url):
    """Faz download da imagem externa e salva no ImageField do produto."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        nome_arquivo = os.path.basename(urlparse(url).path) or "imagem.jpg"
        produto.imagem.save(nome_arquivo, ContentFile(response.content), save=True)

    except requests.RequestException as e:
        raise ApiError({"imagem": f"Erro ao baixar imagem: {e}"}, status=400)


# VALIDAÇÕES DO PRODUTO
def validar_produto(dados, parcial=False):
    erros = {}

    if not parcial or "nome" in dados:
        if not dados.get("nome"):
            erros["nome"] = "Nome é obrigatório"

    if not parcial or "codigo" in dados:
        if not dados.get("codigo"):
            erros["codigo"] = "Código é obrigatório"

    if not parcial or "valor" in dados:
        try:
            valor = Decimal(dados.get("valor"))
            if valor <= 0:
                erros["valor"] = "Valor deve ser maior que zero"
        except (InvalidOperation, TypeError):
            erros["valor"] = "Valor inválido"

    if not parcial or "imagem" in dados:
        if not dados.get("imagem"):
            erros["imagem"] = "URL da imagem obrigatória."

    if erros:
        raise ApiError(erros, status=400)

# DEFINIÇÕES DO CRUD
@transaction.atomic
def criar_produto(dados):
    imagem_url=dados.get("imagem", "")
    
    produto = Produto.objects.create(
        nome=dados["nome"],
        codigo=dados["codigo"],
        valor=dados["valor"],
        imagem_url=imagem_url
    )

    # if imagem_url:
    #     _baixar_e_salvar_imagem(produto, imagem_url)

    return produto.id


@transaction.atomic
def atualizar_produto(produto, dados):
    nova_url = dados.get("imagem")
    url_mudou = nova_url and nova_url != produto.imagem_url
    
    for campo in ["nome", "codigo", "valor", "imagem"]:
        if campo in dados:
            setattr(produto, campo, dados[campo]) if campo != "imagem" else setattr(produto, "imagem_url", dados[campo])

    produto.data_alteracao = timezone.now()
    produto.save()

    # if url_mudou:
    #     _baixar_e_salvar_imagem(produto, nova_url)


@transaction.atomic
def excluir_produto(produto):
    produto.excluido = True
    produto.save()