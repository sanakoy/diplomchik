from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import models

class Plan(models.Model):
    precent = models.FloatField(default=0)
    # is_global = models.BooleanField(default=False)
    date = models.DateField(auto_now_add=True)
    plan_sum = models.FloatField(default=0)

    def __str__(self):
        return str(self.plan_sum)
class Category(models.Model):
    name = models.CharField(max_length=100)
    cat_sum = models.FloatField(default=0)
    # parent = models.ForeignKey("Category", on_delete=models.CASCADE, blank=True, null=True)
    is_profit = models.BooleanField(default=False)
    date_create = models.DateTimeField(blank=True, null=True)
    date_upd_cat_sum = models.DateTimeField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    plan = models.OneToOneField(Plan, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, default=None)

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




