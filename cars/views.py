from django.shortcuts import render
from cars.models import Car

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
