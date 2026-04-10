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
    # Giraffe.query.create(primary_key="test")


giraffe_2 = Giraffe.query.with_fields(Giraffe.primary_key.label("new_label")).latest("date")

if giraffe_2:
    # Cannot fix type hints here without a Mypy or Pyright plugin (for more than 1 field)
    print(giraffe_2[0].capitalize())

giraffe_3 = Giraffe.query.load_fields(Giraffe.primary_key).latest("date")

if giraffe_3:
    print(giraffe_3.primary_key.capitalize())

Giraffe.query.update({Giraffe.number: Giraffe.number + 1})

giraffes = Giraffe.query.with_fields(Giraffe.primary_key).offset(1).limit(1).all()
print(giraffes)


print(Migration.query.latest())
