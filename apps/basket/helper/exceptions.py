class PackNotInPackCart(Exception):
    ...


class CartDoesNotExist(Exception):
    ...


class DuplicatePackCartInCart(Exception):
    ...


class OrderFailedToCreate(Exception):
    ...


class OrderFailedToFinalize(Exception):
    ...


class FailedAddToCart(Exception):
    ...


class FailedRefund(Exception):
    ...
