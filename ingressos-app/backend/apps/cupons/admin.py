from django.contrib import admin

from .models import Cupom


@admin.register(Cupom)
class CupomAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "tipo_desconto",
        "valor",
        "validade",
        "ativo",
        "quantidade_usos",
        "limite_usos",
    )
    list_filter = (
        "tipo_desconto",
        "ativo",
    )
    search_fields = ("codigo",)
