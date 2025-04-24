from django.shortcuts import render
from cars.models import Car

# Create your views here.
def car_view(request):
    # cars = Car.objects.filter(brand__name='Chevrolet')
    cars = Car.objects.filter(model__icontains='onix')

    return render(request,
                  'cars.html',
                  {'cars': cars}
                  )
