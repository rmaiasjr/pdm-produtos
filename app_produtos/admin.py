from django.contrib import admin
from .models import Produto

@admin.register(Produto)
class ChaveAPIAdmin(admin.ModelAdmin):
    """Área gestão dos produtos."""
    list_display = ('nome', 'codigo', 'valor', 'excluido')
    readonly_fields = ('imagem',)
    list_filter = ('excluido',)
    search_fields = ('nome', 'codigo')
