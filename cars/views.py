from django.shortcuts import render
from cars.models import Car

# Create your views here.
def car_view(request):
    cars = Car.objects.all()
    print(cars)

    return render(request,
                  'cars.html',
                  {'cars': cars}
                  )
