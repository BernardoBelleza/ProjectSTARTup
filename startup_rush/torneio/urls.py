from django.urls import path
from . import views

app_name = 'torneio'

urlpatterns = [
    path('', views.listar_startups, name='home'),
    path('cadastro/', views.cadastro_startup, name='cadastro_startup'),
    path('startups/', views.listar_startups,    name='listar_startups'),
    path(
      'iniciar/',
      views.iniciar_torneio,
      name='iniciar_torneio'
    ),
    # # path('listar_batalhas/', views.listar_batalhas,  name='listar_batalhas'),
    # path(
    # 'rodada/<int:rodada_numero>/batalhas/',
    # views.listar_batalhas,
    # name='listar_batalhas'
    # ),
    
    path(
    'batalhas/',
    views.listar_batalhas,     # agora a view não recebe rodada_numero
    name='listar_batalhas'
    ),
    path(
      'batalha/<int:batalha_id>/administrar/',
      views.administrar_batalha,
      name='administrar_batalha'
    ),
    # path('historico/<int:numero>/', views.historico_torneio,
    #  name='historico_torneio'),
    path('historico/', views.historico_torneios, name='historico_torneios'),

    # path(
    #     'batalha/<int:batalha_id>/encerrar/',
    #     views.encerrar_batalha,
    #     name='encerrar_batalha'
    # ),
]