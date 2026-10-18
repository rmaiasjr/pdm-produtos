from django.db import models
from decimal import Decimal
from django.core.exceptions import ValidationError

from django.core.validators import MinValueValidator

class Pedido(models.Model):
    data_emissao = models.DateTimeField(auto_now_add=True)
    ultima_alteracao = models.DateTimeField(auto_now=True)
    excluido = models.BooleanField(default=False)
    cliente = models.ForeignKey('clientes.Cliente', 
                                on_delete=models.PROTECT,
                                related_name="pedidos")

    def __str__(self):
        return f"{self.id} - {self.cliente}"

class ItemPedido(models.Model):

    class NivelRentabilidade(models.TextChoices):
        RUIM = 'RUIM', 'Ruim'
        BOA = 'BOA', 'Boa'
        OTIMA = 'OTIMA', 'Ótima'
    
    pedido = models.ForeignKey(Pedido,
                               on_delete=models.CASCADE,
                               related_name="itens")
    produto = models.ForeignKey('app_produtos.Produto',
                                on_delete=models.PROTECT,
                                related_name="itens_pedido")
    quantidade = models.PositiveIntegerField(default=1,
                                             validators=[MinValueValidator(1)])
    preco_bruto = models.DecimalField(max_digits=10, 
                                      decimal_places=2,
                                      validators=[MinValueValidator(Decimal('0.01'))])
    preco_liquido = models.DecimalField(max_digits=10, 
                                        decimal_places=2,
                                        validators=[MinValueValidator(Decimal('0.01'))])
    nivel_rentabilidade = models.CharField(max_length=5,
                                           blank=True,
                                           choices=NivelRentabilidade.choices)
    excluido = models.BooleanField(default=False)


    def calcular_nivel_rentabilidade(self):
        limite_boa = self.preco_bruto * Decimal('0.90')
        if self.preco_liquido > self.preco_bruto:
            return self.NivelRentabilidade.OTIMA
        if self.preco_liquido >= limite_boa:
            return self.NivelRentabilidade.BOA
        return self.NivelRentabilidade.RUIM

    def clean(self):
        erros = {}

        # Só valida as regras se os campos básicos estiverem preenchidos
        if self.preco_bruto is not None and self.preco_liquido is not None:
            nivel = self.calcular_nivel_rentabilidade()
            if nivel == self.NivelRentabilidade.RUIM:
                erros['preco_liquido'] = (
                    'Rentabilidade ruim: o preço não pode ser mais de 10% '
                    'menor que o preço do produto.')
            else:
                self.nivel_rentabilidade = nivel

        if self.produto_id and self.quantidade:
            multiplo = self.produto.multiplo
            if multiplo and self.quantidade % multiplo != 0:
                erros['quantidade'] = (
                    f'Este produto só pode ser vendido em múltiplos de {multiplo}.')

        if erros:
            raise ValidationError(erros)