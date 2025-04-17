from django.shortcuts import render, redirect
from .models import Startup, Rodada, Batalha
from .forms import StartupForm
import random
from django.http import HttpResponse


def cadastro_startup(request):
    form = StartupForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('torneio:listar_startups')
    return render(request, 'torneio/cadastro_startup.html', {
        'form': form
    })

def listar_startups(request):
    startups = Startup.objects.all()
    count = startups.count()
    foiValidado = (4 <= count <= 8) and (count % 2 == 0)
    return render(request, 'torneio/listar_startups.html', {
        'startups': startups,
        'foiValidado': foiValidado,
    })

def iniciar_torneio(request):
    # 1) Validação de número de startups
    count = Startup.objects.count()
    if not (4 <= count <= 8 and count % 2 == 0):
        return render(request, 'torneio/listar_startups.html', {
            'startups': Startup.objects.all(),
            'foiValidado': False,
            'error': 'Cadastre entre 4 e 8 startups em número par para iniciar.'
        })

    proximaRodada = Rodada.objects.count() + 1
    rodada = Rodada.objects.create(numeroDaRodada=proximaRodada)


    startups = list(Startup.objects.all())
    random.shuffle(startups)

    # Enquanto ainda houver startups na lista...
    while startups:
        grupo1 = startups.pop(0)
        grupo2 = startups.pop(0)

        Batalha.objects.create(
            primeiraStartup=grupo1,
            segundaStartup=grupo2,
            rodada=rodada
        )


     # agora sim redireciona para listar batalhas dessa rodada
    return redirect('torneio:listar_batalhas', rodada_numero=rodada.numeroDaRodada)


def listar_batalhas(request, rodada_numero):
    # filtra todas que casem com o número; pode retornar lista vazia
    rodadas = Rodada.objects.filter(numeroDaRodada=rodada_numero)
    # if not rodadas:
    #     return HttpResponse("Rodada não encontrada", status=404)

    # pega o primeiro (e único) elemento da lista
    rodada = rodadas[0]
    batalhas = rodada.batalha_set.all()
    return render(request, 'torneio/listar_batalhas.html', {
        'rodada': rodada,
        'batalhas': batalhas,
    })
