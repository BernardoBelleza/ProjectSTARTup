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
    # path('listar_batalhas/', views.listar_batalhas,  name='listar_batalhas'),
    path(
    'rodada/<int:rodada_numero>/batalhas/',
    views.listar_batalhas,
    name='listar_batalhas'
    ),
]