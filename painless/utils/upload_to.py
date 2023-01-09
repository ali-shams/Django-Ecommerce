from django.contrib.sites.models import Site

from datetime import (
    datetime,
    date
)


def category_dir_path(instance,
                      filename):
    categories = instance.product.category.get_ancestors(include_self=True)
    categories_path = "/".join(
        [category.title[:5].strip() if len(category.title) > 5 else category.title.strip() for category in
         categories])
    return "category/{}/prod-{}/{}".format(categories_path,
                                           instance.product.title[:55].strip() if
                                           len(instance.product.title) > 54 else instance.product.title.strip(),
                                           filename)


def user_directory_path(instance,
                        filename):
    return "user_{}/{}".format(instance.user,
                               filename)


def date_directory_path(filename):
    today = date.today()
    return f"{today.year}/{today.month}/{today.day}/{filename}"
