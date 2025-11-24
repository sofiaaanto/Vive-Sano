from django.urls import path
from . import views

urlpatterns = [
    path("registrar/", views.registrar, name="registrar"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("admin-panel/", views.admin_panel, name="admin_panel"),
]
