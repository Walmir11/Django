from django.shortcuts import render
from cars.models import Car
from cars.forms import CarForm

# Create your views here.
def car_view(request):
    cars = Car.objects.all().order_by('model')
    search = request.GET.get('search')

    if search:
        cars = Car.objects.filter(model__icontains=search).order_by('model')

    return render(request,
                  'cars.html',
                  {'cars': cars}
                  )

def new_car_view(request):
    new_car_form = CarForm()
    return render(request, 'new_car.html', {'new_car_form': new_car_form})