from django.urls import path
from .views import pedidos_view, rentabilidade_view

urlpatterns = [
    path('pedidos/', pedidos_view),
    path('pedidos/<int:pedido_id>', pedidos_view),
    path('pedidos/rentabilidade/', rentabilidade_view),
]