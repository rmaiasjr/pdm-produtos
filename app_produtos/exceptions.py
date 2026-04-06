class ApiError(Exception):
    """Base para erros da API com status HTTP."""
    def __init__(self, mensagem, status=400):
        self.mensagem = mensagem
        self.status = status
        super().__init__(mensagem)

class NaoEncontrado(ApiError):
    def __init__(self, recurso="Recurso"):
        super().__init__(f"{recurso} não encontrado", status=404)

class IdObrigatorio(ApiError):
    def __init__(self):
        super().__init__("ID é obrigatório", status=400)

class MetodoNaoPermitido(ApiError):
    def __init__(self):
        super().__init__("Método não permitido", status=405)