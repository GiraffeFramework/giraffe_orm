from giraffe_orm import db
from django.db import models


class Django(models.Model):
    primary_key = models.CharField(primary_key=True)

    
django = Django.objects.latest()
django.primary_key = "test"
django.save()


class Giraffe(db.Model):
    primary_key = db.String(primary_key=True, min_length=0, max_length=10)
    date = db.Date()

giraffe = Giraffe.query.latest(Giraffe.date)

if giraffe:
    giraffe.primary_key = "Amazing"
    giraffe.save()