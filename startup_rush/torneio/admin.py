from django.contrib import admin

from django.contrib import admin
from .models import Startup, Rodada, Batalha, Evento

admin.site.register(Startup)
admin.site.register(Rodada)
admin.site.register(Batalha)
admin.site.register(Evento)
