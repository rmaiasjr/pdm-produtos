from django.contrib import admin
from .models import ChaveAPI

@admin.register(ChaveAPI)
class ChaveAPIAdmin(admin.ModelAdmin):
    """Área para criação da chave de acesso a api."""
    list_display = ('descricao', 'ativa', 'data_criacao', 'data_expiracao')
    readonly_fields = ('chave', 'data_criacao')
    list_filter = ('ativa',)
    search_fields = ('chave', 'descricao')