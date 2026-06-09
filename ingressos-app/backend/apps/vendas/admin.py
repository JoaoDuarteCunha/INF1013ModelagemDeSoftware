from django.contrib import admin

from .models import Venda, Ingresso


@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "usuario",
        "sessao",
        "status",
        "valor_final",
        "criada_em",
    )
    list_filter = ("status", "canal")


@admin.register(Ingresso)
class IngressoAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "venda",
        "assento_sessao",
        "tipo",
        "preco",
    )
