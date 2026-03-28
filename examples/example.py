# from django.db import models
# class Django(models.Model):
#     primary_key = models.CharField(primary_key=True)

    
# django = Django.objects.latest()
# django.primary_key = "test"
# django.save()

from .models import Giraffe


giraffe = Giraffe.query.latest(Giraffe.date)
print(giraffe)

giraffe_2 = Giraffe.query.latest("date")
print(giraffe_2)


if giraffe:
    # new_giraffe = Giraffe.query.create()

    giraffe.primary_key = "Amazing"
    # giraffe.save()
