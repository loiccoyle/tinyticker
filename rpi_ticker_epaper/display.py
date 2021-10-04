import logging
from typing import Callable



CURRENCY_SYMBOLS = {"USD": "$"}


def default_delta_func(delta: float, _: float) -> str:
    if delta < 0:
        out = "-"
    elif delta == 0:
        out = "="
    else:
        out = "+"
    return out


class Display:
    pass
# class Display:
#     """Handle the displaying of the API response.

#     Args:
#         i2c_address: i2c address, see the i2cdetect shell command.
#         delta_func: Callable which should take the change in price and the
#             current price and return a string.
#         string_format: Python format string.
#     """

#     def __init__(
#         self,
#         i2c_address: int = I2C_ADDRESS,
#         delta_func: Callable[[float, float], str] = default_delta_func,
#         string_format: str = "{delta}{coin}:{currency} {price}",
#     ) -> None:
#         self._log = logging.getLogger(__name__)
#         self.i2c_address = i2c_address
#         self.lcd = lcd.HD44780(self.i2c_address)
#         self.delta_func = delta_func
#         self.string_format = string_format
#         self.previous_response = {}

#     def get_delta_string(self, coin: str, prices: dict) -> str:
#         """Determine the up down character indicator.

#         Args:
#             coin: Coin ticker string.
#             prices: Dictionary containing the currencies and prices.

#         Returns:
#             The change indicator character.
#         """
#         if coin not in self.previous_response.keys():
#             self.previous_response[coin] = prices
#             out = "?"
#         else:
#             prices_prev = self.previous_response[coin]
#             # compute the difference on just one currency
#             price = list(prices.values())[0]
#             delta = price - list(prices_prev.values())[0]
#             self._log.debug("%s delta: %f", coin, delta)
#             out = self.delta_func(delta, price)
#             # update the previous response
#             self.previous_response[coin] = prices
#         self._log.debug("%s delta string: %s", coin, out)
#         return out

#     def display_string(self, coin: str, prices: dict) -> str:
#         """Construct the display string.

#         Args:
#             coin: Coin ticker string.
#             prices: Dictionary containing the currencies and prices.

#         Returns:
#             Display string.
#         """
#         currency, amount = list(prices.items())[0]
#         currency_str = CURRENCY_SYMBOLS.get(currency, currency)
#         delta_str = self.get_delta_string(coin, prices)
#         display_str_no_price = self.string_format.replace("{price}", "").format(
#             delta=delta_str, coin=coin, currency=currency_str
#         )
#         price_str = str(amount)
#         n_padding = 16 - len(display_str_no_price)
#         if n_padding > 0:
#             price_str = "{amount:>{padding}}".format(amount=amount, padding=n_padding)
#         return self.string_format.format(
#             delta=delta_str, coin=coin, currency=currency_str, price=price_str
#         )

#     def show(self, response: dict) -> None:
#         """Display the API response on the display.

#         Args:
#             response: The API response.
#         """
#         for i, (coin, prices) in enumerate(response.items(), start=1):
#             display_str = self.display_string(coin, prices)
#             self._log.info("Current line: %i", i)
#             self._log.info("Display string: %s", display_str)
#             self.lcd.set(display_str, i)
