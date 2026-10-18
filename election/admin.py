from django.contrib import admin

from .models import AnnouncedPuResults, Lga, PollingUnit

admin.site.register(Lga)
admin.site.register(PollingUnit)
admin.site.register(AnnouncedPuResults)
