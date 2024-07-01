from tinyticker import layouts

from .utils import DIMENSIONS, LAYOUT_DIR, layout_test


def test_default(ticker_response):
    layout_test(layouts.default, DIMENSIONS, ticker_response, LAYOUT_DIR)


def test_big_price(ticker_response):
    layout_test(layouts.big_price, DIMENSIONS, ticker_response, LAYOUT_DIR)


def test_logo(ticker_response):
    layout_test(layouts.logo, DIMENSIONS, ticker_response, LAYOUT_DIR)
