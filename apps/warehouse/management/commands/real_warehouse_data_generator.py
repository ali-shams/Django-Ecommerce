import logging

from django.core.management.base import BaseCommand

from warehouse.repository.generator_layer import RealWarehouseDataGenerator

RDGL = RealWarehouseDataGenerator()
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Real Data Generator
    Generate data for warehouse app.
    """
    help = 'Generate real data for Warehouse APP.'

    def add_arguments(self, parser):
        parser.add_argument('--total-colors',
                            type=int,
                            default=20,
                            help='Specify the number of colors to generate.')
        parser.add_argument('--total-warranties',
                            type=int,
                            default=20,
                            help='Specify the number of warranties to generate.')
        parser.add_argument('--total-tags',
                            type=int,
                            default=50,
                            help='Specify the number of tags to generate.')
        parser.add_argument('--total-packs',
                            type=int,
                            default=4,
                            help='Specify the maximum number of packs per product to generate.')  # noqa

    def handle(self, *args, **kwargs):
        total_colors = kwargs['total_colors']
        total_warranties = kwargs['total_warranties']
        total_tags = kwargs['total_tags']
        total_packs = kwargs['total_packs']

        logger.debug('Prepare to generate fake data  ...')

        brands = RDGL.create_brands()
        self.stdout.write(self.style.SUCCESS(f'{len(brands)} brands have been generated by machine.'))  # noqa

        categories = RDGL.create_categories()
        self.stdout.write(self.style.SUCCESS(f'{len(categories)} categories have been generated by machine.'))  # noqa

        colors = RDGL.create_colors(total_colors)
        self.stdout.write(self.style.SUCCESS(f'{len(colors)} colors have been generated by machine.'))  # noqa

        warranties = RDGL.create_warranties(total_warranties)
        self.stdout.write(self.style.SUCCESS(f'{len(warranties)} warranties have been generated by machine.'))  # noqa

        tags = RDGL.create_tags(total_tags)
        self.stdout.write(self.style.SUCCESS(f'{len(tags)} tags have been generated by machine.'))  # noqa

        products, all_products_from_excel, products_sheet_names = RDGL.create_products(tags)
        self.stdout.write(self.style.SUCCESS(f'{len(products)} products have been generated by machine.'))  # noqa

        RDGL.create_physical_info(products, all_products_from_excel)
        self.stdout.write(
            self.style.SUCCESS(f'One physical information per product have been generated by machine.'))  # noqa

        packs = RDGL.create_packs(colors, warranties, products, all_products_from_excel, total_packs)
        self.stdout.write(
            self.style.SUCCESS(f'Maximum of {total_packs} packs per product have been generated by machine.'))  # noqa

        RDGL.create_expenses(packs)
        self.stdout.write(self.style.SUCCESS(f'One expense per pack were priced by machine.'))  # noqa

        RDGL.create_product_gallery(products, all_products_from_excel, products_sheet_names)  # noqa
        self.stdout.write(self.style.SUCCESS(f'Some pictures have been generated by machine.'))  # noqa

        logger.debug('Real data generation finished.')