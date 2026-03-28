# from django.db import models
# class Django(models.Model):
#     primary_key = models.CharField(primary_key=True)

    
# django = Django.objects.latest()
# django.primary_key = "test"
# django.save()

from giraffe_orm import db


class Giraffe(db.Model):
    primary_key = db.String(primary_key=True, min_length=0, max_length=10)
    date = db.Date()


giraffe = Giraffe.query.latest(Giraffe.date)
print(giraffe)

giraffe_2 = Giraffe.query.latest("date")
print(giraffe_2)


if giraffe:
    # new_giraffe = Giraffe.query.create()

    giraffe.primary_key = "Amazing"
    # giraffe.save()
