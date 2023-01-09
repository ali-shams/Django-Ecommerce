import os
import re
import logging
import random

from unidecode import unidecode
from tqdm import tqdm
from django.utils.text import slugify
from django.core.files.uploadedfile import SimpleUploadedFile

import dataset
from dataset import ReadDataset
from kernel.settings.packages import CURRENCIES
from kernel.settings.base import BASE_DIR
from painless.repository.base import BaseDataGenerator
from warehouse.models import (
    Brand,
    Category,
    Color,
    Warranty,
    Tag,
    Product,
    PhysicalInformation,
    Pack,
    Expense,
    ProductGallery
)

logger = logging.getLogger(__name__)


class RealWarehouseDataGenerator(BaseDataGenerator):
    def atoi(self, text):
        return int(text) if text.isdigit() else text

    def natural_keys(self, text):
        '''
        alist.sort(key=natural_keys) sorts in human order
        http://nedbatchelder.com/blog/200712/human_sorting.html
        (See Toothy's implementation in the comments)
        '''
        return [self.atoi(c) for c in re.split(r'(\d+)', text)]

    def get_title(self,
                  prefix='obj',
                  total=50):
        return [
            f'{prefix}-{self.get_random_secret(20)}'
            for _ in range(total)
        ]

    def get_categories(self,
                       categories,
                       disable_progress_bar,
                       level):
        return [Category(sku=self.get_random_secret(20),
                         title=category['title_en'],
                         title_fa=category['title_fa'],
                         title_en=category['title_en'],
                         slug=slugify(category['title_fa'], allow_unicode=True),
                         is_active=category['is_active'],
                         is_shippable=category['is_shippable'],
                         is_color_important=category['is_color_important'],
                         is_virtual=category['is_virtual'],
                         is_downloadable=category['is_downloadable'],
                         level=category['level'],
                         lft=category['lft'],
                         rght=category['rght'],
                         tree_id=category['tree_id'])
                for category in tqdm(categories, disable=disable_progress_bar) if category['level'] == level  # noqa
                ]

    def get_parent_id_grand_children(self,
                                     categories,
                                     grand_children_cat_objs):  # noqa
        count_level_one = -1
        grand_children_cat_objs_parent_ids = list()
        for cat in categories:
            if cat['level'] == 1:
                count_level_one += 1
            elif cat['level'] == 2:
                grand_children_cat_objs_parent_ids.append(count_level_one)
        return grand_children_cat_objs_parent_ids

    def create_brands(self,
                      batch_size=300,
                      disable_progress_bar=False):
        """Create fake data for `Brand` model
        PARAMS
        ------
        total : int
        The number of Brand to create.
        batch_size : int
        The number of objects to be added to the database
        """
        brands = ReadDataset.read_excel_file('brands')
        brand_objs = [Brand(title=brand['title_en'],
                            slug=slugify(brand['title_en'], allow_unicode=True))
                      for brand in tqdm(brands, disable=disable_progress_bar)
                      ]

        logger.debug(f'{len(brand_objs)} brand objects created successfully.')
        Brand.objects.bulk_create(brand_objs, batch_size=batch_size)
        logger.debug('All brands are saved into the database.')
        brands = Brand.objects.all()
        return brands

    def create_categories(self,
                          batch_size=300,
                          disable_progress_bar=False):
        """Create fake data for `Category` model
        PARAMS
        ------
        total : int
        The number of Category to create.
        batch_size : int
        The number of objects to be added to the database
        """
        categories = ReadDataset.read_excel_file('categories')

        parent_cat_objs = self.get_categories(categories, disable_progress_bar=disable_progress_bar, level=0)  # noqa
        logger.debug(f'{len(parent_cat_objs)} parent category objects created successfully.')  # noqa
        Category.tree.bulk_create(parent_cat_objs, batch_size=batch_size)  # noqa
        logger.debug('All parent categories are saved into the database.')

        children_cat_objs = self.get_categories(categories, disable_progress_bar=disable_progress_bar, level=1)  # noqa
        logger.debug(f'{len(children_cat_objs)} child category objects created successfully.')  # noqa
        for child in children_cat_objs:
            parent_id = child.tree_id
            child.insert_at(parent_cat_objs[parent_id], position='last-child', save=True)  # noqa
        logger.debug('All child categories are saved into the database.')

        grand_children_cat_objs = self.get_categories(categories, disable_progress_bar=disable_progress_bar, level=2)
        grand_children_cat_objs_parent_ids = self.get_parent_id_grand_children(categories, grand_children_cat_objs)
        logger.debug(f'{len(grand_children_cat_objs)} grand child category objects created successfully.')  # noqa
        for index, grand_child in enumerate(grand_children_cat_objs):
            parent_id = grand_children_cat_objs_parent_ids[index]
            grand_child.insert_at(children_cat_objs[parent_id], position='last-child', save=True)
        logger.debug('All grand child categories are saved into the database.')

        categories = Category.objects.all()
        return categories

    def create_colors(self,
                      total,
                      batch_size=300,
                      disable_progress_bar=False):
        """Create fake data for `Color` model
        PARAMS
        ------
        total : int
        The number of Color to create.
        batch_size : int
        The number of objects to be added to the database
        """
        titles = self.get_title(prefix='CL', total=total)
        color_objs = [Color(title=title,
                            hex_code=self.get_random_hex_code())
                      for title in tqdm(titles, disable=disable_progress_bar)
                      ]

        logger.debug(f'{len(color_objs)} color objects created successfully.')
        Color.objects.bulk_create(color_objs, batch_size=batch_size)
        logger.debug('All colors are saved into the database.')
        colors = Color.objects.all()
        return colors

    def create_warranties(self,
                          total,
                          batch_size=300,
                          disable_progress_bar=False):
        """Create fake data for `Warranty` model
        PARAMS
        ------
        total : int
        The number of Product to create.
        batch_size : int
        The number of objects to be added to the database
        """
        titles = self.get_title(prefix='WR', total=total)
        warranty_objs = [Warranty(title=title)
                         for title in tqdm(titles, disable=disable_progress_bar)
                         ]

        logger.debug(f'{len(warranty_objs)} warranty objects created successfully.')
        Warranty.objects.bulk_create(warranty_objs, batch_size=batch_size)
        logger.debug('All warranties are saved into the database.')
        warranties = Warranty.objects.all()
        return warranties

    def create_tags(self,
                    total,
                    batch_size=300,
                    disable_progress_bar=False):
        """Create fake data for `Tag` model
        PARAMS
        ------
        total : int
        The number of Tags to create.
        batch_size : int
        The number of objects to be added to the database
        """
        titles = self.get_title(prefix='TG', total=total)
        tag_objs = [Tag(title=title,
                        slug=slugify(title, allow_unicode=True))
                    for title in tqdm(titles, disable=disable_progress_bar)
                    ]

        logger.debug(f'{len(tag_objs)} tag objects created successfully.')
        Tag.objects.bulk_create(tag_objs, batch_size=batch_size)
        logger.debug('All tags are saved into the database.')
        tags = Tag.objects.all()
        return tags

    def create_products(self,
                        tags,
                        tag_count=5,
                        product_with_no_tag_ratio=2,
                        batch_size=300,
                        disable_progress_bar=False):
        """Create fake data for `Product` model
        PARAMS
        ------
        total : int
        The number of Product to create.
        batch_size : int
        The number of objects to be added to the database
        """
        products_sheet_names = ReadDataset.get_sheet_names()
        all_products_from_excel = list()
        for prod_sheet_name in products_sheet_names:
            if 'prod' in prod_sheet_name:
                prods = ReadDataset.read_excel_file(prod_sheet_name)
                brand_obj = Brand.objects.get(title=prods[0]['brand']) if prods[0]['brand'] is not None else None
                category_obj = Category.objects.get(title=prods[0]['category']) if \
                    prods[0]['category'] is not None else None
                [prod.update(brand=brand_obj) for prod in prods]
                [prod.update(category=category_obj) for prod in prods]
                all_products_from_excel += prods

        product_objs = [Product(sku=self.get_random_secret(20),
                                title=product['title_en'],
                                title_fa=product['title_fa'],
                                title_en=product['title_en'],
                                slug=slugify(product['title_fa'], allow_unicode=True),
                                description=self.get_random_sentence(),
                                subtitle=product['subtitle'],
                                is_active=product['is_active'],
                                is_voucher_active=product['is_voucher_active'],
                                brand=product['brand'],
                                category=product['category'])
                        for product in tqdm(all_products_from_excel, disable=disable_progress_bar)
                        ]

        logger.debug(f'{len(product_objs)} product objects created successfully.')
        Product.objects.bulk_create(product_objs, batch_size=batch_size)
        products = Product.objects.all()

        product_objs = random.sample(list(products), len(product_objs) // product_with_no_tag_ratio)
        [product_obj.tags.set(random.sample(list(tags), random.randint(1, tag_count)))
         for product_obj in product_objs]
        logger.debug('All products are saved into the database.')
        return products, all_products_from_excel, products_sheet_names

    def create_physical_info(self,
                             products,
                             all_products_from_excel,
                             batch_size=300,
                             disable_progress_bar=False):
        """Create_physical_info
        creates fake data for physical_info model. it creates a data
        for each product.
        PARAMS
        ------
        batch_size : int
        The number of objects to be added to the database
        """
        physical_info_objs = [PhysicalInformation(height=float(unidecode(product['dimensions'].split('x')[0])),
                                                  width=float(unidecode(product['dimensions'].split('x')[1])),
                                                  depth=float(unidecode(product['dimensions'].split('x')[2])),
                                                  net_weight=float(unidecode(product['net_weight'])),
                                                  gross_weight=self.get_random_float(1, 10),
                                                  product=product_obj)
                              for product_obj, product in
                              tqdm(zip(products, all_products_from_excel), disable=disable_progress_bar) if
                              'dimensions' and 'net_weight' in product.keys()
                              ]

        logger.debug(f'{len(products)} physical information objects created successfully.')  # noqa
        PhysicalInformation.objects.bulk_create(physical_info_objs, batch_size=batch_size)  # noqa
        logger.debug('All physical information are saved into the database.')

    def create_packs(self,
                     colors,
                     warranties,
                     products,
                     all_products_from_excel,
                     total,
                     batch_size=300,
                     disable_progress_bar=False):
        """Create fake data for `Pack` model

        PARAMS
        ------
        `total` : int
            The number of Packs to create.
        `batch_size` : int
            The number of objects to be added to the database
        """
        pack_objs_not_one_pack = [Pack(sku=self.get_random_secret(20),
                                       is_active=True if i == 0 else self.get_random_boolean(),
                                       is_default=True if i == 0 else False,
                                       color=random.choice(colors),
                                       warranty=random.choice(warranties),
                                       product=product_obj)
                                  for product_obj, product in
                                  tqdm(zip(products, all_products_from_excel), disable=disable_progress_bar) if
                                  'has_one_pack' not in product.keys()
                                  for i in range(random.randint(1, total))
                                  ]
        pack_objs_one_pack = [Pack(sku=self.get_random_secret(20),
                                   is_active=self.get_random_boolean(),
                                   is_default=True,
                                   product=product_obj)
                              for product_obj, product in
                              tqdm(zip(products, all_products_from_excel), disable=disable_progress_bar) if
                              'has_one_pack' in product.keys()
                              ]

        all_packs_objs = pack_objs_not_one_pack + pack_objs_one_pack
        logger.debug(f'Maximum of {total} packs are made per product.')
        Pack.objects.bulk_create(all_packs_objs, batch_size=batch_size)
        logger.debug('All packs are saved into the database.')
        packs = Pack.objects.all()
        return packs

    def create_expenses(self,
                        packs,
                        rial_profit=(1.7, 1.9),
                        toman_profit=(1.2, 1.4),
                        usd_profit=(1.1, 1.2),
                        batch_size=300,
                        disable_progress_bar=False):
        """Create fake data for `Pack` model
        PARAMS
        ------
        `batch_size` : int
            The number of objects to be added to the database
        """
        expense_objs = [Expense(buy_price=self.get_random_price(),
                                buy_price_currency=random.choice(CURRENCIES),
                                count_stock=random.randint(0, 500),
                                actual_count_stock=random.randint(0, 250),
                                is_suppliable=self.get_random_boolean(),
                                pack=pack)
                        for pack in tqdm(packs, disable=disable_progress_bar)
                        ]

        for expense_obj in expense_objs:
            expense_obj.price_currency = expense_obj.buy_price_currency
            expense_obj.price = self.get_currency_exchange(expense_obj.buy_price_currency,
                                                           expense_obj.buy_price.amount,
                                                           rial_profit,
                                                           toman_profit,
                                                           usd_profit)

        logger.debug(f'{len(expense_objs)} expense objects created successfully.')
        Expense.objects.bulk_create(expense_objs, batch_size=batch_size)
        logger.debug('All expenses are saved into the database.')

    def create_product_gallery(self,
                               products,
                               all_products_from_excel,
                               products_sheet_names,
                               disable_progress_bar=False):
        picture_objs = []
        products = iter(products)
        for prod_sheet_name in products_sheet_names:
            if 'prod' in prod_sheet_name:
                prod_path = os.path.normpath(f'{dataset.__path__[0]}/products/{prod_sheet_name}')
                sub_dirs = sorted(list(map(int, [f.name for f in os.scandir(prod_path) if f.is_dir()])))
                all_sub_dirs = [os.path.normpath(f'{prod_path}/{sub_dir}') for sub_dir in sub_dirs]
                for dir in all_sub_dirs:
                    product = next(products)
                    all_dir_image_name = [dirs[2] for dirs in os.walk((dir))][0]
                    if not all_dir_image_name:
                        all_sub_dirs_images = [os.path.normpath(f'{dataset.__path__[0]}/default_image.jpg')]
                    else:
                        all_dir_image_name.sort(key=self.natural_keys)
                        all_sub_dirs_images = [os.path.normpath(f'{dir}/{image_name}') for image_name in
                                               all_dir_image_name]
                    picture_objs += [ProductGallery(product=product,
                                                    picture=SimpleUploadedFile(
                                                        name=self.get_path(image_path)[0].name,
                                                        content=self.get_path(image_path)[1]),
                                                    alternate_text=self.get_random_sentence()[:110],
                                                    image_status=self.get_image_banner(index),
                                                    is_default=True if index == 0 else False)
                                     for index, image_path in enumerate(all_sub_dirs_images)
                                     ]

        logger.info(f'{len(picture_objs)} picture objects created in Product Gallery.')  # noqa
        ProductGallery.objects.bulk_create(picture_objs)
        logger.info('All pictures are saved into the database.')

    def get_path(self, image_path):
        with open(os.path.join(BASE_DIR, os.path.normpath(image_path)), 'rb') as image_file:  # noqa
            result = (image_file, image_file.read())
        return result
