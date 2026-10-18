from django.db import models

class Produto(models.Model):
    nome = models.CharField(max_length=100)
    codigo = models.CharField(max_length=50)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    excluido = models.BooleanField(default=False)
    ultma_alteracao = models.DateTimeField(auto_now=True)
    imagem_url = models.URLField()
    imagem = models.ImageField(upload_to='produtos/', null=True, blank=True)
    multiplo = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.codigo} - {self.nome}"