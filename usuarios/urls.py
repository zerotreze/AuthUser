from django.urls import path
from . import views

urlpatterns = [
    path('cadastro/', views.cadastro, name="cadastro"), # type: ignore
    path('logar/', views.logar, name="logar"), # type: ignore
    
]