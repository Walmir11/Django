from django.urls import path
from django.contrib.auth import views as auth_views
from .views import CadastroClienteView, CadastroProfissionalView, PainelView

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    path("cadastro/cliente/", CadastroClienteView.as_view(), name="cadastro_cliente"),
    path("cadastro/profissional/", CadastroProfissionalView.as_view(), name="cadastro_profissional"),

    path("painel/", PainelView.as_view(), name="painel"),
]