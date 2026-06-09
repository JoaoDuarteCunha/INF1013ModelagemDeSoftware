from django.contrib import admin

from .models import Pagamento


@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "venda",
        "forma",
        "status",
        "valor",
        "criado_em",
    )
    list_filter = ("forma", "status")
