from django.db import models

class Startup(models.Model):
    nome      = models.CharField(max_length=50)
    slogan    = models.CharField(max_length=250)
    anoFundacao  = models.PositiveIntegerField()
    pontos    = models.IntegerField(default=70)

class Rodada(models.Model):
    numeroDaRodada    = models.PositiveIntegerField()
    startups = models.ManyToManyField(Startup)

class Batalha(models.Model):
    primeiraStartup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name='primeiraStarBatalhas')
    segundaStartup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name='segundaStarBatalhas')
    rodada    = models.ForeignKey(Rodada, on_delete=models.CASCADE)
    concluida = models.BooleanField(default=False)
    vencedor  = models.ForeignKey(
        Startup,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='batalhasVencidas'
    )

class Evento(models.Model):
    POSSIVEIS_EVENTOS = [
        ('PITCH',     'Pitch convincente'),
        ('BUGS',       'Produto com bugs'),
        ('TRACAO',    'Boa tração de usuários'),
        ('INVESTIRRITADO',    'Investidor irritado'),
        ('FAKENEWS',  'Fake news no pitch'),
    ]
    batalha = models.ForeignKey(Batalha, on_delete=models.CASCADE)
    tipo    = models.CharField(max_length=15, choices=POSSIVEIS_EVENTOS)
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE)



    