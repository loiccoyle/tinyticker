import os
from io import BytesIO
from pathlib import Path

import matplotlib.pyplot as plt

UPDATE_REF_PLOTS = os.environ.get("TINYTICKER_UPDATE_REF_PLOTS", False)


def expected_fig(fig: plt.Figure, reference: Path) -> bool:
    """Helper function to compare the generated plot with the reference plot."""
    if UPDATE_REF_PLOTS:
        fig.savefig(reference, format="png")
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return reference.open("rb").read() == buf.read()
