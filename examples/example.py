# from django.db import models
# class Django(models.Model):
#     primary_key = models.CharField(primary_key=True)

    
# django = Django.objects.latest()
# django.primary_key = "test"
# django.save()

from giraffe_orm.defaults import Migration

from .models import Giraffe


giraffe = Giraffe.query.latest(Giraffe.date)
print(giraffe)

if giraffe:
    giraffe.primary_key.capitalize()

    giraffe.primary_key = "amazing"
    giraffe.date = "tomorrow"
    giraffe.save()

else:
    print("???")
    Giraffe.query.create(primary_key="test")


giraffe_2 = Giraffe.query.latest("date")
print(giraffe_2)


print(Migration.query.latest())
