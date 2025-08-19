from django.urls import path
from .views import CadastroClienteView, CadastroProfissionalView, PainelView
from accounts.views import login_view, logout_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    path("cadastro/cliente/", CadastroClienteView.as_view(), name="cadastro_cliente"),
    path("cadastro/profissional/", CadastroProfissionalView.as_view(), name="cadastro_profissional"),

    path("painel/", PainelView.as_view(), name="painel"),

]