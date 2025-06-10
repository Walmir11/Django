from django.views.generic import ListView, CreateView, DetailView
from cars.models import Car
from cars.forms import CarModelForm

class CarsListView(ListView):
    model = Car
    template_name = 'cars.html'
    context_object_name = 'cars'

    def get_queryset(self):
        cars = super().get_queryset().order_by('model')
        search = self.request.GET.get('search')
        if search:
            cars = cars.filter(model__icontains=search)
        return cars

class NewCarCreateView(CreateView):
    model = Car
    form_class = CarModelForm
    template_name = 'new_car.html'
    success_url = '/cars/'

class CarDetailView(DetailView):
    model = Car
    template_name = 'car_detail.html'



# Forma antiga
# def car_view(request):
#     cars = Car.objects.all().order_by('model')
#     search = request.GET.get('search')
#
#     if search:
#         cars = Car.objects.filter(model__icontains=search).order_by('model')
#
#     return render(request,
#                   'cars.html',
#                   {'cars': cars}
#                   )

# def new_car_view(request):
#     if request.method == "POST":
#         new_car_form = CarModelForm(request.POST, request.FILES)
#         if new_car_form.is_valid():
#             new_car_form.save()
#             return redirect('car_list')
#         else:
#             print(new_car_form.errors)
#     else:
#         new_car_form = CarModelForm()
#     return render(request, 'new_car.html', {'new_car_form': new_car_form})