from django.utils import timezone
from django.db import models

class Plan(models.Model):
    precent = models.FloatField(default=0)
    is_global = models.BooleanField(default=False)
    date = models.DateField(auto_now_add=True)
    plan_sum = models.FloatField(default=0)

    def __str__(self):
        return str(self.plan_sum)
class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey("Category", on_delete=models.CASCADE, blank=True, null=True)
    is_profit = models.BooleanField(default=False)
    plan = models.OneToOneField(Plan, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name

class Operation(models.Model):
    sum = models.FloatField(default=0)
    comment = models.CharField(max_length=100, default='', blank=True, null=True)
    # date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    kod_cat = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        if self.comment == None:
            return str(self.sum)
        return str(self.sum) + ' ' + self.comment


class Profit(models.Model):
    comment = models.CharField(max_length=100)
    sum = models.FloatField(default=0)
    date = models.DateTimeField("Дата расхода")
    kod_cat = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.sum



