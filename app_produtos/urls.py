from django.urls import path
from .view import produtos_view

urlpatterns = [
    path('produtos/', produtos_view),
    path('produtos/<int:produto_id>', produtos_view)
]