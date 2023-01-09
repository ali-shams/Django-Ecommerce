import logging

from django.core.management import call_command
from django.core.management.base import BaseCommand

from account.management.commands.account_data_generator import Command as AccountCommand
from warehouse.management.commands.warehouse_data_generator import Command as WarehouseCommand

class Command(BaseCommand):
    """
    Generates mock data for all models and a superuser.
    """
    help = 'Generate data for all models and also adds a superuser'

    def handle(self, *args, **kwargs):
        call_command('warehouse_data_generator')
        call_command('account_data_generator')
        call_command('logistic_data_generator')
        call_command('basket_data_generator')
        call_command('voucher_data_generator')
        call_command('Banner_data_generator')
        call_command('feedback_data_generator')
        call_command('demo_user_generator')
