from django.conf import settings

from django.db.models import (
                        F,
                        Case,
                        When)

from painless.models.fields import MoneyCurrencyOutput


def convert_currency(self,
                     output_currency=settings.DEFAULT_CURRENCY_SHOW_ON_SITE):
    """
    Converts the price of all packs to the given currency,
    stores it in `converted_price` attribute.
    """
    # TODO: make this method accept PackCart and Pack.
    exchange_rates = {
        'USD': {
            'R': 400000,
            'T': 40000,
        },
        'R': {
            'USD': 2.5e-06,
            'T': 0.1,
        },
        'T': {
            'USD': 2.5e-05,
            'R': 10,
        }
    }
    if output_currency.upper() not in exchange_rates.keys():
        raise ValueError(f'given currency: `{output_currency}` '
                         f'not in accepted currencies: {exchange_rates.keys()}')
    else:
        output_currency = output_currency.upper()
    my_list = list()
    if type(self).__name__ == 'ExpenseQuerySet':
        for currency in exchange_rates.keys():
            if currency == output_currency:
                rate = 1
            else:
                rate = exchange_rates[currency][output_currency]
            my_list.append(
                When(price_currency=currency, then=F('price') * rate),
            )
        qs = self.annotate(
                converted_price=Case(
                    *my_list,
                    output_field=MoneyCurrencyOutput(output_currency)
                    )
                )
    elif type(self).__name__ == 'PackQuerySet':
        for currency in exchange_rates.keys():
            if currency == output_currency:
                rate = 1
            else:
                rate = exchange_rates[currency][output_currency]
            my_list.append(
                When(expense__price_currency=currency, then=F('expense__price') * rate),
            )
        qs = self.annotate(
                converted_price=Case(
                    *my_list,
                    output_field=MoneyCurrencyOutput(output_currency)
                )
            )
    elif type(self).__name__ in ['PackCartQuerySet', 'PackOrderQuerySet']:
        for currency in exchange_rates.keys():
            if currency == output_currency:
                rate = 1
            else:
                rate = exchange_rates[currency][output_currency]
            my_list.append(
                When(pack__expense__price_currency=currency, then=F('pack__expense__price') * rate),
            )
        qs = self.annotate(
                converted_price=Case(
                    *my_list,
                    output_field=MoneyCurrencyOutput(output_currency)
                )
            )

    else:
        raise ValueError(f'{self} does not have access to convert_currency.')
    return qs
