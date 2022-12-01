import matplotlib as mpl


def set_color_scheme() -> None:
    colors = ["#ffb14e", "ea5f94", "4228d7", "1d1c1c"]
    mpl.rcParams["axes.prop_cycle"] = mpl.cycler(color=colors)
