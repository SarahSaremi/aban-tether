from django.db import models


class Account(models.Model):
    username = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    joined_date = models.DateField(auto_now_add=True)


class Wallet(models.Model):
    account = models.OneToOneField(to='account.Account', on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2)  # Used DecimalField to prevent float rounding issues

    def withdraw(self, price):
        if self.balance >= price:
            self.balance -= price
            self.save()
            return True
        return False

    def deposit(self, price):
        self.balance += price
        self.save()
