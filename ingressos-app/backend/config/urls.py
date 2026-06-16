from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.catalogo.views import FilmeViewSet
from apps.cinemas.views import CinemaViewSet, SalaViewSet
from apps.assentos.views import AssentoViewSet
from apps.sessoes.views import SessaoViewSet
from apps.vendas.views import VendaViewSet
from apps.cupons.views import CupomViewSet

router = DefaultRouter()
router.register(r"filmes", FilmeViewSet)
router.register(r"cinemas", CinemaViewSet)
router.register(r"salas", SalaViewSet)
router.register(r"assentos", AssentoViewSet)
router.register(r"sessoes", SessaoViewSet, basename="sessao")
router.register(r"vendas", VendaViewSet, basename="venda")
router.register(r"cupons", CupomViewSet, basename="cupom")

urlpatterns = [
    path("", include("apps.core.urls")),
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path(
        "api-auth/",
        include("rest_framework.urls"),
    ),
]
