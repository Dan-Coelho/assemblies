from django.urls import path
from . import views

urlpatterns = [
    # Criar item de pauta em uma assembleia
    path(
        'assembleias/<uuid:assembly_pk>/pauta/novo/',
        views.AgendaItemCreateView.as_view(),
        name='agenda_item_create',
    ),
    # Atualizar item de pauta
    path(
        'assembleias/<uuid:assembly_pk>/pauta/<uuid:pk>/editar/',
        views.AgendaItemUpdateView.as_view(),
        name='agenda_item_update',
    ),
    # Abrir votação do item (pending → open)
    path(
        'assembleias/<uuid:assembly_pk>/pauta/<uuid:pk>/abrir/',
        views.AgendaItemOpenView.as_view(),
        name='agenda_item_open',
    ),
    # Encerrar votação do item (open → closed)
    path(
        'assembleias/<uuid:assembly_pk>/pauta/<uuid:pk>/encerrar/',
        views.AgendaItemCloseView.as_view(),
        name='agenda_item_close',
    ),
    # Tela de votação (GET) e registro de voto (POST)
    path(
        'assembleias/<uuid:assembly_pk>/pauta/<uuid:item_pk>/votar/',
        views.CastVoteView.as_view(),
        name='cast_vote',
    ),
]
