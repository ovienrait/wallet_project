from django.db import models

DEFAULT_BALANCE = 0


class Wallet(models.Model):
    '''Модель кошелька с уникальным идентификатором и балансом.'''
    uuid = models.CharField(max_length=36, primary_key=True)
    balance = models.PositiveBigIntegerField(default=DEFAULT_BALANCE)

    def __str__(self):
        return f'Wallet: {self.uuid} - Balance: {self.balance}'
