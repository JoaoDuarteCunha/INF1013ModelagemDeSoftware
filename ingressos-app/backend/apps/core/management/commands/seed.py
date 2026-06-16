from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.assentos.models import Assento
from apps.catalogo.models import Filme
from apps.cinemas.models import Cinema, Sala
from apps.cupons.models import Cupom
from apps.sessoes.models import Sessao


class Command(BaseCommand):
    help = "Popula o banco com dados iniciais para demonstração."

    def handle(self, *args, **options):
        self.criar_usuario_teste()
        filmes = self.criar_filmes()
        cinema, sala = self.criar_cinema_sala()
        self.criar_assentos(sala)
        self.criar_sessoes(filmes, sala)
        self.criar_cupons()

        self.stdout.write(self.style.SUCCESS("Seed executado com sucesso."))

    def criar_usuario_teste(self):
        User = get_user_model()

        usuario, criado = User.objects.get_or_create(
            username="cliente",
            defaults={
                "email": "cliente@teste.com",
                "first_name": "Cliente",
                "last_name": "Teste",
            },
        )

        if criado:
            usuario.set_password("cliente123")
            usuario.save()
            self.stdout.write("Usuário cliente criado.")
        else:
            self.stdout.write("Usuário cliente já existia.")

        admin, criado = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@teste.com",
                "is_staff": True,
                "is_superuser": True,
            },
        )

        if criado:
            admin.set_password("admin123")
            admin.save()
            self.stdout.write("Usuário admin criado.")
        else:
            self.stdout.write("Usuário admin já existia.")

    def criar_filmes(self):
        dados_filmes = [
            {
                "nome": "Interestelar",
                "genero": "Ficção científica",
                "sinopse": "Uma equipe viaja pelo espaço em busca de um novo lar para a humanidade.",
                "duracao_minutos": 169,
                "formato": "IMAX",
            },
            {
                "nome": "Homem-Aranha: Através do Aranhaverso",
                "genero": "Animação",
                "sinopse": "Miles Morales embarca em uma aventura pelo multiverso.",
                "duracao_minutos": 140,
                "formato": "2D",
            },
            {
                "nome": "Avatar: O Caminho da Água",
                "genero": "Aventura",
                "sinopse": "Jake Sully e sua família exploram novas regiões de Pandora.",
                "duracao_minutos": 192,
                "formato": "3D",
            },
        ]

        filmes = []

        for dados in dados_filmes:
            filme, criado = Filme.objects.update_or_create(
                nome=dados["nome"],
                defaults=dados,
            )
            filmes.append(filme)

            if criado:
                self.stdout.write(f"Filme criado: {filme.nome}")
            else:
                self.stdout.write(f"Filme atualizado: {filme.nome}")

        return filmes

    def criar_cinema_sala(self):
        cinema, _ = Cinema.objects.update_or_create(
            cnpj="12.345.678/0001-90",
            defaults={
                "nome": "Cinema INF1013",
                "endereco": "Rua da Modelagem, 1013",
            },
        )

        sala, _ = Sala.objects.update_or_create(
            cinema=cinema,
            nome="Sala 1",
            defaults={
                "capacidade": 40,
                "suporta_2d": True,
                "suporta_3d": True,
                "suporta_4d": False,
                "suporta_imax": True,
            },
        )

        self.stdout.write("Cinema e sala criados/atualizados.")

        return cinema, sala

    def criar_assentos(self, sala):
        filas = ["A", "B", "C", "D"]
        numeros = range(1, 11)

        total = 0

        for fila in filas:
            for numero in numeros:
                _, criado = Assento.objects.get_or_create(
                    sala=sala,
                    fila=fila,
                    numero=numero,
                )

                if criado:
                    total += 1

        self.stdout.write(
            f"Assentos criados: {total}. Total da sala: {sala.assentos.count()}."
        )

    def criar_sessoes(self, filmes, sala):
        agora = timezone.now()

        horarios = [
            agora + timedelta(days=1, hours=2),
            agora + timedelta(days=1, hours=5),
            agora + timedelta(days=2, hours=3),
        ]

        for index, filme in enumerate(filmes):
            inicio = horarios[index]
            fim = inicio + timedelta(minutes=filme.duracao_minutos)

            sessao, criado = Sessao.objects.update_or_create(
                filme=filme,
                sala=sala,
                inicio=inicio,
                defaults={
                    "fim": fim,
                    "preco_base": Decimal("30.00") + Decimal(index * 5),
                    "ativa": True,
                },
            )

            if criado:
                self.stdout.write(f"Sessão criada: {sessao}")
            else:
                self.stdout.write(f"Sessão atualizada: {sessao}")

    def criar_cupons(self):
        validade = timezone.now() + timedelta(days=30)

        cupons = [
            {
                "codigo": "PROMO20",
                "tipo_desconto": Cupom.TipoDesconto.PERCENTUAL,
                "valor": Decimal("20.00"),
                "validade": validade,
                "ativo": True,
                "limite_usos": 100,
            },
            {
                "codigo": "FIXO10",
                "tipo_desconto": Cupom.TipoDesconto.FIXO,
                "valor": Decimal("10.00"),
                "validade": validade,
                "ativo": True,
                "limite_usos": 50,
            },
        ]

        for dados in cupons:
            cupom, criado = Cupom.objects.update_or_create(
                codigo=dados["codigo"],
                defaults=dados,
            )

            if criado:
                self.stdout.write(f"Cupom criado: {cupom.codigo}")
            else:
                self.stdout.write(f"Cupom atualizado: {cupom.codigo}")
