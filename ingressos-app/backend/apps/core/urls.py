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
]
