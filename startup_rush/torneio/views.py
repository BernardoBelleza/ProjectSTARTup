from django.shortcuts import render, redirect
from .models import Startup, Rodada, Batalha, Evento, Torneio, TorneioStats
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
    
     # 2) Busca a última rodada, se existir
    # pega quantas rodadas já existem
    numero_de_rodadas = Rodada.objects.count()

    if numero_de_rodadas == 0:
        # ultima = 1
        rodada = Rodada.objects.create(numeroDaRodada=1)
    else:
        # pega todas as rodadas em um QuerySet (que por padrão vem ordenado pelo id, 
        # o que equivale à ordem de criação) e acessa pelo índice
        return redirect('torneio:listar_batalhas')
        # todas = Rodada.objects.all()
        # ultima = todas[numero_de_rodadas - 1]
        # rodada = Rodada.objects.create(numeroDaRodada=ultima.numeroDaRodada)
    # ultima = Rodada.objects.order_by('-numeroDaRodada').first()

    # proximaRodada = Rodada.objects.count() + 1
    # rodada = Rodada.objects.create(numeroDaRodada=ultima.numeroDaRodada)


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
    # return redirect('torneio:listar_batalhas', rodada_numero=rodada.numeroDaRodada)
    return redirect('torneio:listar_batalhas')

# def listar_batalhas(request, rodada_numero):
#     # filtra todas que casem com o número; pode retornar lista vazia
#     rodadas = Rodada.objects.filter(numeroDaRodada=rodada_numero)
#     # if not rodadas:
#     #     return HttpResponse("Rodada não encontrada", status=404)

#     # pega o primeiro (e único) elemento da lista
#     rodada = rodadas[0]
#     batalhas = rodada.batalha_set.all()
#     return render(request, 'torneio/listar_batalhas.html', {
#         'rodada': rodada,
#         'batalhas': batalhas,
#     })

def listar_batalhas(request):
    """
    • Mostra todas as batalhas já criadas.
    • Se a última rodada terminou:
        – Se sobram ≥2 vencedores → cria próxima rodada.
        – Se sobrou 1 vencedor   → mostra estatísticas finais.
    """
    rodadas = list(Rodada.objects.order_by('numeroDaRodada'))
    estatisticas = None      # continuará None até ter campeão
    campea       = None        # ← inicializa aqui!
    
    if rodadas:
        ultima = rodadas[-1]
        pendentes = Batalha.objects.filter(rodada=ultima, concluida=False).exists()

        print("PENDENTES:", pendentes)   # ← 1ª impressão

        if not pendentes:
            # vencedores da última rodada
            vencedores = [b.vencedor for b in Batalha.objects.filter(rodada=ultima)]

            print("VENCEDORES:", vencedores)   # ← 2ª impressão

            if len(vencedores) > 1:
                # -------- cria próxima rodada com os vencedores --------
                proximo_num = ultima.numeroDaRodada + 1
                prox = Rodada.objects.filter(numeroDaRodada=proximo_num).first()
                if not prox:
                    prox = Rodada.objects.create(numeroDaRodada=proximo_num)
                    random.shuffle(vencedores)
                    while vencedores:
                        s1 = vencedores.pop(0)
                        s2 = vencedores.pop(0)
                        Batalha.objects.create(
                            primeiraStartup=s1,
                            segundaStartup=s2,
                            rodada=prox
                        )
                rodadas.append(prox)          # para exibir no template
            else:
                # -------- torneio acabou: gera estatísticas finais --------
                estatisticas = gerar_estatisticas_por_eventos()

                print("ESTATISTICAS:", estatisticas)  # ← 3ª impressão

                if estatisticas:
                    campea = estatisticas[0]['startup']          # ranking não vazio
                else:
                    campea = vencedores[0]  

                quantosTiveram = Torneio.objects.count()

                # próximo número é sempre +1
                numero_do_torneio = quantosTiveram + 1

                # numero_do_torneio = Torneio.objects.count()        # ou outro critério
                # campea = estatisticas[0]['startup']               # primeiro da lista

                if not Torneio.objects.filter(numero=numero_do_torneio).exists():
                    torneio = Torneio.objects.create(numero=numero_do_torneio, campea=campea)
                else:
                    torneio = Torneio.objects.get(numero=numero_do_torneio)

                # torneio = Torneio.objects.create(
                #     numero=numero_do_torneio,
                #     campea=campea
                # )
                if not torneio.statsJaSalvos:
                    for d in estatisticas:
                        TorneioStats.objects.create(
                            torneio      = torneio,
                            startup      = d['startup'],
                            pontos       = d['pontos'],
                            pitches      = d['pitches'],
                            bugs         = d['bugs'],
                            tracoes      = d['tracoes'],
                            investidores = d['investidores'],
                            penalidades  = d['penalidades'],
                        )
                    torneio.statsJaSalvos = True
                    torneio.save()

    # monta lista de rodadas + batalhas
    todas_rodadas = []
    for r in rodadas:
        batalhas = list(Batalha.objects.filter(rodada=r))
        todas_rodadas.append({'rodada': r, 'batalhas': batalhas})

    return render(request, 'torneio/listar_batalhas.html', {
        'todas_rodadas': todas_rodadas,
        'estatisticas': estatisticas,     # None ou lista de stats
        'campea'       : campea,         # sempre envia a campeã
    })

def administrar_batalha(request, batalha_id):
    # 1) Buscar batalha
    try:
        batalha = Batalha.objects.get(pk=batalha_id)
    except Batalha.DoesNotExist:
        return HttpResponse("Batalha não encontrada", status=404)

    # 2) Carregar eventos já salvos
    eventos = Evento.objects.filter(batalha=batalha)

    if request.method == 'POST':
        # Captura qual botão foi clicado
        acao = request.POST.get('acao')

        # 3) Registrar todos os checkboxes marcados
        #    request.POST.getlist('eventos') devolve lista de strings "startupId:TIPO"
        marcados = request.POST.getlist('eventos')
        for item in marcados:
            startup_id, tipo = item.split(':')
            # Evita duplicar o mesmo evento duas vezes
            existe = Evento.objects.filter(
                batalha=batalha,
                startup_id=startup_id,
                tipo=tipo
            ).exists()
            if not existe:
                Evento.objects.create(
                    batalha=batalha,
                    startup_id=startup_id,
                    tipo=tipo
                )

        # 4) Se clicou em “Encerrar Batalha”, calcula vencedor
        if acao == 'encerrar':
            # Pontuações por tipo
            valores = {
                'PITCH': 6,
                'BUGS': -4,
                'TRACAO': 3,
                'INVESTIRRITADO': -6,
                'FAKENEWS': -8,
            }
            # inicializa placar
            placar = {
                batalha.primeiraStartup.id: 0,
                batalha.segundaStartup.id:  0,
            }
            # soma eventos
            for ev in Evento.objects.filter(batalha=batalha):
                placar[ev.startup.id] += valores[ev.tipo]

            # desempate Shark Fight
            id1 = batalha.primeiraStartup.id
            id2 = batalha.segundaStartup.id
            if placar[id1] == placar[id2]:
                escolhido = random.choice([id1, id2])
                placar[escolhido] += 2

            # define vencedor
            vencedor_id = id1 if placar[id1] > placar[id2] else id2
            vencedor = Startup.objects.get(pk=vencedor_id)

            # salva vencedor e soma 30 pontos
            batalha.vencedor = vencedor
            batalha.concluida = True
            batalha.save()

            vencedor.pontos += 30
            vencedor.save()

            # redireciona para a listagem da rodada
            return redirect(
                'torneio:listar_batalhas',
                # rodada_numero=batalha.rodada.numeroDaRodada
            )

        # Se foi apenas “Salvar Eventos”, recarrega a página pra ver o histórico
        return redirect('torneio:administrar_batalha', batalha_id=batalha.id)

    # 5) GET: exibe o formulário
    tipos_de_evento = Evento.POSSIVEIS_EVENTOS
    participantes   = [batalha.primeiraStartup, batalha.segundaStartup]

    return render(request, 'torneio/administrar_batalha.html', {
        'batalha': batalha,
        'eventos': eventos,
        'tipos_de_evento': tipos_de_evento,
        'participantes': participantes,
    })


def gerar_estatisticas_por_eventos():
    """
    Percorre TODA a tabela Evento e devolve
    uma lista de stats ordenada por pontos decrescente.
    """
    stats = {}  # chave: startup_id  →  valor: dicionário de contadores

    # 1) percorre cada linha da tabela Evento
    for ev in Evento.objects.select_related('startup'):
        sid = ev.startup_id

        # se a startup não está no dicionário, cria a estrutura
        if sid not in stats:
            stats[sid] = {
                'startup': ev.startup,   # objeto Startup já carregado
                'pontos':  ev.startup.pontos,
                'pitches': 0,
                'bugs': 0,
                'tracoes': 0,
                'investidores': 0,
                'penalidades': 0,
            }

        # incrementa o contador correto
        if ev.tipo == 'PITCH':
            stats[sid]['pitches'] += 1
        elif ev.tipo == 'BUGS':
            stats[sid]['bugs'] += 1
        elif ev.tipo == 'TRACAO':
            stats[sid]['tracoes'] += 1
        elif ev.tipo == 'INVESTIRRITADO':
            stats[sid]['investidores'] += 1
        elif ev.tipo == 'FAKENEWS':
            stats[sid]['penalidades'] += 1

    # 2) transforma em lista e ordena pelos pontos finais
    lista_stats = list(stats.values())
    lista_stats.sort(key=lambda d: d['pontos'], reverse=True)
    return lista_stats

def historico_torneios(request):
    torneios = Torneio.objects.order_by('-numero')   # sempre mostrado
    numero = request.GET.get('numero')               # opcional

    torneio = None
    estatisticas = None

    torneio = Torneio.objects.filter(numero=numero).first()  # devolve objeto ou None

    if numero:                                       # usuário escolheu algo?
        torneio = Torneio.objects.filter(numero=numero).first()
        if torneio is None:                          # número inválido
            return HttpResponse("Torneio não encontrado", status=404)
        estatisticas = torneio.estatisticas.order_by('-pontos')

    return render(request, 'torneio/historico.html', {
        'torneios'    : torneios,
        'torneio'     : torneio,       # None ou objeto
        'stats': estatisticas,  # None ou ranking
    })

# def administrar_batalha(request, batalha_id):
#     # 1) Buscar a batalha ou retornar 404 simples
#     try:
#         batalha = Batalha.objects.get(pk=batalha_id)
#     except Batalha.DoesNotExist:
#         return HttpResponse("Batalha não encontrada", status=404)

#     # 2) Se vier POST, registra um novo evento
#     if request.method == 'POST':
#         # ler os valores enviados pelo form
#         startup_id = request.POST.get('startup')
#         tipo_evento = request.POST.get('tipo')

#         # buscar a startup selecionada
#         try:
#             startup = Startup.objects.get(pk=startup_id)
#         except Startup.DoesNotExist:
#             return HttpResponse("Startup inválida", status=400)

#         # criar e salvar o Evento
#         evento = Evento(
#             batalha=batalha,
#             startup=startup,
#             tipo=tipo_evento
#         )
#         evento.save()

#         # após salvar, recarrega a mesma página para listar de novo
#         return redirect('torneio:administrar_batalha', batalha_id=batalha.id)

#     # 3) Para GET, buscar todos os eventos dessa batalha
#     eventos = Evento.objects.filter(batalha=batalha)

#     # 4) Preparar listas para o form manual
#     #    - tipos de evento (tuplas do modelo)
#     tipos_de_evento = Evento.POSSIVEIS_EVENTOS
#     #    - startups que participam desta batalha
#     participantes = [
#         batalha.primeiraStartup,
#         batalha.segundaStartup
#     ]

#     # 5) Renderizar o template com tudo no contexto
#     return render(request, 'torneio/administrar_batalha.html', {
#         'batalha': batalha,
#         'eventos': eventos,
#         'tipos_de_evento': tipos_de_evento,
#         'participantes': participantes,
#     })




# def encerrar_batalha(request, batalha_id):
#     # 1) carrega a batalha
#     try:
#         batalha = Batalha.objects.get(pk=batalha_id)
#     except Batalha.DoesNotExist:
#         return HttpResponse("Batalha não encontrada", status=404)

#     # 2) pega todos os eventos dessa batalha
#     eventos = Evento.objects.filter(batalha=batalha)

#     # inicializa o placar das duas startups
#     placar = {
#         batalha.primeiraStartup.id: 0,
#         batalha.segundaStartup.id:  0,
#     }

#     # para cada evento, calcula quantos pontos vale
#     for evento in eventos:
#         tipo_evento     = evento.tipo              # ex: 'PITCH', 'BUGS', ...
#         startup_id      = evento.startup.id        # ID da startup que recebeu o evento

#         # atribui manualmente o valor de cada tipo
#         if tipo_evento == 'PITCH':
#             pontos = 6
#         elif tipo_evento == 'BUGS':
#             pontos = -4
#         elif tipo_evento == 'TRACAO':
#             pontos = 3
#         elif tipo_evento == 'INVESTIRRITADO':
#             pontos = -6
#         elif tipo_evento == 'FAKENEWS':
#             pontos = -8
#         else:
#             pontos = 0

#         # acumula no placar daquela startup
#         placar[startup_id] = placar[startup_id] + pontos

#     # 3) desempate “Shark Fight”
#     id1 = batalha.primeiraStartup.id
#     id2 = batalha.segundaStartup.id
#     if placar[id1] == placar[id2]:
#         vencedor_id = random.choice([id1, id2])
#         placar[vencedor_id] += 2
#     else:
#         vencedor_id = id1 if placar[id1] > placar[id2] else id2

#     vencedor = Startup.objects.get(pk=vencedor_id)

#     # 4) marca vitória e atualiza pontos persistentes
#     batalha.vencedor  = vencedor
#     batalha.concluida = True
#     batalha.save()

#     vencedor.pontos += 30
#     vencedor.save()

#     # 5) volta para a listagem de batalhas da mesma rodada
#     return redirect(
#         'torneio:listar_batalhas',
#         rodada_numero=batalha.rodada.numeroDaRodada
#     )