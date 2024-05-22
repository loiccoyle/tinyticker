from datetime import timezone

import pandas as pd

from tinyticker import utils

# monkey patch the now function so tests are time indenpendent
utils.__dict__["now"] = lambda: pd.Timestamp(
    2021, 7, 22, 18, 00, 00, tzinfo=timezone.utc
)
