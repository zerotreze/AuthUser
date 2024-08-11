from django.urls import path
from . import views


urlpatterns = [
    path('sugestao/', views.sugestao, name="sugestao"), # type: ignore
    path('ver_empresa/<int:id>', views.ver_empresa, name="ver_empresa"),
    path('realizar_proposta/<int:id>', views.realizar_proposta, name="realizar_proposta"),
    path('assinar_contrato/<int:id>', views.assinar_contrato, name="assinar_contrato")


]
