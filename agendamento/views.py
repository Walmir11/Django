from django.views.generic import ListView
from .models import Servico

# Create your views here.

class HomePageView(ListView):
    """
    View para a página inicial que lista todos os serviços disponíveis.
    """
    model = Servico
    template_name = 'home.html'
    context_object_name = 'servicos' # Nome da variável no template
