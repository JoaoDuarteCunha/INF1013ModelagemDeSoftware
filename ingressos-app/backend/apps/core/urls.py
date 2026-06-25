from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("filmes/<int:filme_id>/", views.filme_detalhe, name="filme_detalhe"),
    path("sessoes/<int:sessao_id>/", views.sessao_detalhe, name="sessao_detalhe"),
    path(
        "sessoes/<int:sessao_id>/reservar/",
        views.reservar_assentos_front,
        name="reservar_assentos_front",
    ),
    path(
        "sessoes/<int:sessao_id>/reserva/",
        views.reserva_detalhe,
        name="reserva_detalhe",
    ),
    path(
        "sessoes/<int:sessao_id>/confirmar-compra/",
        views.confirmar_compra_front,
        name="confirmar_compra_front",
    ),
    path(
        "minhas-compras/",
        views.minhas_compras,
        name="minhas_compras",
    ),
    path(
        "minhas-compras/<int:venda_id>/",
        views.venda_detalhe_front,
        name="venda_detalhe_front",
    ),
    path(
        "minhas-compras/<int:venda_id>/cancelar/",
        views.cancelar_venda_front,
        name="cancelar_venda_front",
    ),
    path("minhas-reservas/", views.minhas_reservas, name="minhas_reservas"),
    path("login/", views.login_front, name="login_front"),
    path("logout/", views.logout_front, name="logout_front"),
]
