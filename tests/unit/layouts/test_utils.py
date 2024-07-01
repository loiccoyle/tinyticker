from tinyticker.layouts import utils


def test_create_fig_ax():
    dimensions = (250, 122)
    fig, axes = utils.create_fig_ax(dimensions, 2)
    assert len(axes) == 2
    for ax in axes:
        assert ax.margins() == (0, 0)
        assert ax.axison is False
    assert (fig.get_size_inches() * fig.dpi == dimensions).all()
