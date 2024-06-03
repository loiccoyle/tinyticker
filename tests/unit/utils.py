import os
from io import BytesIO
from pathlib import Path

from matplotlib.figure import Figure

UPDATE_REF_PLOTS = os.environ.get("TINYTICKER_UPDATE_REF_PLOTS", False)


def expected_fig(fig: Figure, reference: Path) -> bool:
    """Helper function to compare the generated plot with the reference plot."""
    if UPDATE_REF_PLOTS:
        fig.savefig(reference, format="jpg")
    buf = BytesIO()
    fig.savefig(buf, format="jpg")
    buf.seek(0)
    return reference.open("rb").read() == buf.read()
