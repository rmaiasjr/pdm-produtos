from django.urls import path
from .views import clientes_view

urlpatterns = [
    path('clientes/', clientes_view),
    path('clientes/<int:cliente_id>', clientes_view),
]