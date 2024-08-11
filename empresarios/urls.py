from django.urls import path
from . import views

urlpatterns = [
    path('cadastrar_empresa/', views.cadastrar_empresa, name='cadastrar_empresa'), # type: ignore
    path('listar_empresas/', views.listar_empresas, name="listar_empresas"), # type: ignore
    path('empresa/<int:id>', views.empresa, name="empresa"), # type: ignore
    path('add_doc/<int:id>', views.add_doc, name="add_doc"),
    path('excluir_dc/<int:id>', views.excluir_dc, name="excluir_dc"),
    path('add_metrica/<int:id>', views.add_metrica, name="add_metrica"),
    path('gerenciar_proposta/<int:id>', views.gerenciar_proposta, name="gerenciar_proposta")


    




]