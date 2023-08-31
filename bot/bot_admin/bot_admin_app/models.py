from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name        


class Subcategory(models.Model):
    name = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.name


class Cart(models.Model):
    user_id = models.CharField(max_length=50)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'User:{self.user_id} - {self.product} - {self.quantity}'


class Subscriber(models.Model):
    chat_id = models.IntegerField(unique=True)
    username = models.CharField(max_length=50)
    phone = models.CharField(max_length=25)
    adress = models.CharField(max_length=200)
    
    def __str__(self):
        return f'{self.username} ({self.chat_id})'
