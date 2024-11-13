from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('cadastrar_usuario/', views.cadastrar_usuario, name='cadastrar_usuario'),
    path('login/', views.login_usuario, name='login_usuario'),
    path('logout/', views.logout_usuario, name='logout_usuario'),
    path('cadastrar_livro/', views.cadastrar_livro, name='cadastrar_livro'),
    path('listar_livros/', views.listar_livros, name='listar_livros'),
    path('consultar_catalogo/', views.consultar_catalogo, name='consultar_catalogo'),
    path('emprestar_livro/', views.emprestar_livro, name='emprestar_livro'),
    path('devolver_livro/', views.devolver_livro, name='devolver_livro'),
    path('reservar_livro/', views.reservar_livro, name='reservar_livro'),
    path('visualizar_multas/', views.visualizar_multas, name='visualizar_multas'),
    path('editar_usuario/<int:usuario_id>/', views.editar_usuario, name='editar_usuario'),
    path('marcar_exemplar_indisponivel/<int:exemplar_id>/', views.marcar_exemplar_indisponivel, name='marcar_exemplar_indisponivel'),
]
