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

---
## 🗂️ Estrutura do Projeto

```
pdm-produtos/
├── produtos/          # Configurações centrais do Django (settings, urls raiz)
├── app_produtos/      # App de CRUD de produtos
├── autenticar/        # App de autenticação
```
---

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
Header: chave=SUA_API_KEY
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


## 🖼️ Upload de Imagens

O serviço PythonAnyWhere no plano gratuíto não suporta requisições para serviços externos. Sendo assim, o upload de aruqivos foi desativado para não gerar erro nas requisições.
O funcionametno pode ser consultado no código comendado no arquivo `services.py` do app `app_produtos`.

---

## 📝 Licença

Este projeto foi desenvolvido para fins educacionais.
