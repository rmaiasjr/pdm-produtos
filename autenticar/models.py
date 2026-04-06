from django.db import models
from django.utils import timezone
from datetime import timedelta
import secrets

class ChaveAPI(models.Model):
    chave = models.CharField(max_length=64, unique=True)
    descricao = models.CharField(max_length=100, blank=True)
    ativa = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_expiracao = models.DateTimeField()

    
    def gerar_chave_api(self):
        return secrets.token_hex(32)
    
    def validar(self):
        return self.ativa and self.data_expiracao > timezone.now()

    def save(self, *args, **kwargs):
        if not self.chave:
            self.chave = self.gerar_chave_api()
            self.data_expiracao = timezone.now() + timedelta(days=60)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.descricao or self.chave
