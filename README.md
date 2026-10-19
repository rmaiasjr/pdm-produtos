# 📦 PDM - API para CRUD de produtos.

A API para gerenciamento de produtos foi desenvolvida com **Django 6** e autenticação por token. O projeto é estruturado em três módulos principais: configuração central (`produtos`), gerenciamento de produtos (`app_produtos`) e autenticação de usuários (`autenticar`).

---

## ⚙️ Tecnologias

- Python 3.13+
- Django 6.0
- SQLite
---
## 📌 Funcionalidades
- Criar produto
- Listar produtos
- Atualizar produtos
- Excluir produtos (soft delete)
- Listar clientes (somente leitura)
- Emitir pedidos com itens
- Consultar pedidos
- Alterar pedidos
- Excluir pedidos (soft delete)

---
## 🗂️ Estrutura do Projeto

```
pdm-produtos/
├── produtos/          # Configurações centrais do Django (settings, urls raiz)
├── app_produtos/      # App de CRUD de produtos (também fornece ApiError, tratar_erros e validar_json)
├── clientes/          # App de consulta de clientes (somente leitura)
├── pedidos/           # App de pedidos e itens de pedido
├── autenticar/        # App de autenticação (middleware da api-key)
```
---
## 🌐 URL base
A URL base a ser utilizada nas requisições é:
``` http
https://rmsjr.pythonanywhere.com
```

## 🔐 Autenticação

Para utilizar a API você precisa de um **Token** fornecido pelo administrador do sistema. Informe a chave no header de todas as requisições.

### Header obrigatório
```http
api-key: SUA_API_KEY
```
---


## 📦 Endpoints de Produtos

### Listar todos os produtos
```http
GET /produtos/
```

#### Resposta:
```json
[
    {
        "id": 1,
        "nome": "Produto 1",
        "codigo": "123456",
        "valor": 12.5,
        "data_alteracao": "2026-04-04T22:03:58.726449+00:00",
        "imagem": ""
    },
    {
        "id": 2,
        "nome": "Produto 2",
        "codigo": "654321",
        "valor": 5.0,
        "data_alteracao": "2026-04-04T21:31:36.131307+00:00",
        "imagem": ""
    }
]
```

---

### Obter produto por ID

```http
GET /produtos/{id}/
```

#### Resposta:
```json
{
    "id": 1,
    "nome": "Produto 1",
    "codigo": "123456",
    "valor": 12.5,
    "data_alteracao": "2026-04-04T22:03:58.726449+00:00",
    "imagem": ""
}
```

---

### Criar produto

```http
POST /produtos/
Content-Type: application/json
```

#### Request
---
*Body*
```json
{
    "nome": "Produto A",
    "codigo": "ABCDE",
    "valor": 5,
    "imagem": ""
}
```

### Resposta

`Status code: 201`
```json
{
  "id": 3
}
```
---

### Atualizar produto
> Envie apenas os campos que deseja alterar.

#### Request

*Body*
```http
PATCH /produtos/{id}/
Content-Type: application/json
```
```json
{
    "nome": "Produto A",
    "codigo": "ABCDE",
    "valor": 5,
    "imagem": ""
}
```
#### Resposta

`Status code: 200`
```json
{
    "mensagem": "Atualizado com sucesso"
}
```
---


### Deletar produto (Soft delete)
> Os itens excluídos não são retornados nas consultas.
```http
DELETE /produtos/{id}/
```
### Resposta
`Status code: 200`

---
## 👥 Endpoints de Clientes

> Somente leitura. Os clientes são pré-cadastrados (Django admin). Qualquer método diferente de `GET` retorna **405**.

### Listar todos os clientes

```
GET /clientes/
```

#### Resposta:

A lista vem ordenada por nome.

```
[
    {
        "id": 1,
        "nome": "Cliente 1"
    },
    {
        "id": 2,
        "nome": "Cliente 2"
    }
]
```

---

### Obter cliente por ID

```
GET /clientes/{id}
```

#### Resposta:

```
{
    "id": 1,
    "nome": "Cliente 1"
}
```

Retorna **404** se o cliente não existir.

---

## 🧾 Endpoints de Pedidos

> As rotas de pedido por ID **não** usam barra no final (`/pedidos/5`, e não `/pedidos/5/`).

### Listar todos os pedidos

```
GET /pedidos/
```

---

### Obter pedido por ID

```
GET /pedidos/{id}
```

Pedido excluído retorna **404**.

---

### Criar pedido

```
POST /pedidos/
Content-Type: application/json
```

#### Request

*Body*

```
{
    "cliente_id": 1,
    "itens": [
        {
            "produto_id": 1,
            "quantidade": 4,
            "preco_liquido": 12.5
        }
    ]
}
```

- `cliente_id`: obrigatório, deve ser um cliente existente.
- `itens`: lista de itens do pedido.
- `produto_id`: deve ser um produto existente e não excluído.
- `quantidade`: inteiro maior que zero e múltiplo do `multiplo` do produto.
- `preco_liquido`: preço unitário informado pelo usuário, maior que zero e com no máximo 2 casas decimais. Se omitido, assume o preço do produto.

#### Resposta

`Status code: 201`

---

### Alterar pedido
> Usa **PUT**: o pedido é substituído por inteiro, então `cliente_id` e `itens` são obrigatórios. **PATCH retorna 405.**

```
PUT /pedidos/{id}
Content-Type: application/json
```

*Body*: mesmo formato da criação.

Os itens atuais são marcados como excluídos (o histórico é preservado) e os novos são criados.

#### Resposta

`Status code: 200`

---

### Deletar pedido (Soft delete)
> Marca o pedido e todos os seus itens ativos como excluídos. Os registros excluídos não são retornados nas consultas.

```
DELETE /pedidos/{id}
```

#### Resposta

`Status code: 200`

---

## 🖼️ Upload de Imagens

O PythonAnyWhere não permite que as aplicações hospedadas no serviço gratuíto façam requisições para servidores externos. Por este motivo, o upload das imagens foi desativado para não gerar erro nas requisições.
O código da conversão da imagem pode ser observado no arquivo `services.py` do app `app_produtos`.
---

## 📝 Licença

Este projeto foi desenvolvido por **Renato Maia** para fins educacionais.
