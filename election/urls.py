from django.urls import path

from . import views

app_name = "election"

urlpatterns = [
    path("", views.polling_unit_result, name="polling_unit_result"),
    path("lga-results/", views.lga_summed_result, name="lga_summed_result"),
    path("add-polling-unit/", views.add_polling_unit, name="add_polling_unit"),
]
