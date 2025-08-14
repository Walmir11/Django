from django.urls import path
from .views import HomePageView

# Adicione aqui as URLs para a página inicial, agendamento, etc.
urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
]