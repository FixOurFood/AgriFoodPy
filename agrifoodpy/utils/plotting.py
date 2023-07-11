import matplotlib.pyplot as plt
import numpy as np

FAOSTAT_elements = ['production',
                    'imports',
                    'exports',
                    'stock',
                    'feed',
                    'seed',
                    'losses',
                    'processing',
                    'residual',
                    'tourist',
                    'domestic',
                    'other',
                    'food',
                    ]

def plot_bars(fbs, show="Item", ax=None, colors=None, labels=None, **kwargs):
    """Horizontal dissagregated bar plot

    Produces a horizontal bar the size of the total quantity summed along the
    coordinates not specified by `show`, and coloured segments to indicate
    the contribution of the each item along the specified `show` coordinate.
    Bars for each dataarray of the dataset have their starting points on the end
    of the previous bar, with `production` and `imports` placed on top, and the
    remaining bars in reverse with `food` placed at the bottom.

    Parameters
    ----------
    food : xarray.Dataset
        Input Dataset containing at least: a `production`, `imports`, `exports`
        and `food` Dataarray
    show : str, optional
        Name of the coordinate to dissagregate when filling the horizontal
        bar. The quantities are summed along the remaining coordinates.
        If the coordinate does not exist in the input, all
        coordinates are summed and a plot with a single color is returned.
    ax : matplotlib.pyplot.artist, optional
        Axes on which to draw the plot. If not provided, a new artist is
        created.
    colors : list of str, optional
        String list containing the colors for each of the elements in the "show"
        coordinate.
        If not defined, a color list is generated from the standard cycling.
    label : list of str, optional
        String list containing the labels for the legend of the elements in the
        "show" coordinate
    **kwargs : dict
        Style options to be passed on to the actual plot function, such as
        linewidth, alpha, etc.

    Returns
    -------
        ax : matplotlib axes instance
    """

    if ax is None:
        f, ax = plt.subplots(**kwargs)

    # Make sure only FAOSTAT food elements are present
    input_elements = list(fbs.keys())
    plot_elements = ["production", "imports", "exports", "food"]

    for element in plot_elements:
        if element not in FAOSTAT_elements:
            plot_elements.remove(element)

    for element in input_elements:
        if element not in plot_elements and element in FAOSTAT_elements:
            plot_elements.insert(-1, element)

    len_elements = len(plot_elements)

    # Define dimensions to sum over
    bar_dims = list(fbs.dims)
    if show in bar_dims:
        bar_dims.remove(show)
        size_show = fbs.sizes[show]
    else:
        size_show = 1

    # Make sure NaN and inf do not interfere
    fbs = fbs.fillna(0)
    fbs = fbs.where(np.isfinite(fbs), other=0)

    food_sum = fbs.sum(dim=bar_dims)

    # If colors are not defined, generate a list from the standard cycling
    if colors is None:
        colors = [f"C{ic}" for ic in range(size_show)]

    # If labels are not defined, generate a list from the dimensions
    if labels is None:
        labels = np.repeat("", len(colors))

    # Plot the production and imports first
    cumul = 0
    for ie, element in enumerate(["production", "imports"]):
        ax.hlines(ie, 0, cumul, color="k", alpha=0.2, linestyle="dashed",
                  linewidth=0.5)
        if size_show == 1:
            ax.barh(ie, left = cumul, width=food_sum[element], color=colors[0])
            cumul +=food_sum[element]
        else:
            for ii, val in enumerate(food_sum[element]):
                ax.barh(ie, left = cumul, width=val, color=colors[ii],
                        label=labels[ii])
                cumul += val

    # Then the rest of elements in reverse to keep dimension ordering
    cumul = 0
    for ie, element in enumerate(reversed(plot_elements[2:])):
        ax.hlines(len_elements-1 - ie, 0, cumul, color="k", alpha=0.2,
                  linestyle="dashed", linewidth=0.5)
        if size_show == 1:
            ax.barh(len_elements-1 - ie, left = cumul, width=food_sum[element],
                    color=colors[0])
            cumul +=food_sum[element]
        else:
            for ii, val in enumerate(food_sum[element]):
                ax.barh(len_elements-1 - ie, left = cumul, width=val,
                        color=colors[ii], label=labels[ii])
                cumul += val

    # Plot decorations
    ax.set_yticks(np.arange(len_elements), labels=plot_elements)
    ax.tick_params(axis="x",direction="in", pad=-12)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_ylim(len_elements+1,-1)

    # Unique labels
    if labels[0] != "":
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), fontsize=6)

    return ax

def plot_years(food, show="Item", ax=None, colors=None, label=None, stack=True,
               **kwargs):
    """ Fill plot with quantities at each year value

    Produces a vertical fill plot with quantities for each year on the "Year"
    coordinate of the input dataset in the horizontal axis. If the "show"
    coordinate exists, then the vertical fill plot is a stack of the sums of
    the other coordinates at that year for each item in the "show" coordinate.

    Parameters
    ----------
    food : xarray.Dataarray
        Input Dataarray containing a "Year" coordinate and optionally, a

    show : str, optional
        Name of the coordinate to dissagregate when filling the vertical
        plot. The quantities are summed along the remaining coordinates.
        If the coordinate is not provided or does not exist in the input, all
        coordinates are summed and a plot with a single fill curve is returned.
    ax : matplotlib.pyplot.artist, optional
        Axes on which to draw the plot. If not provided, a new artist is
        created.
    colors : list of str, optional
        String list containing the colors for each of the elements in the "show"
        coordinate.
        If not defined, a color list is generated from the standard cycling.
    label : list of str, optional
        String list containing the labels for the legend of the elements in the
        "show" coordinate
    **kwargs : dict
        Style options to be passed on to the actual plot function, such as
        linewidth, alpha, etc.

    Returns
    -------
        ax : matplotlib axes instance
    """

    # If no years are found in the dimensions, raise an exception
    sum_dims = list(food.dims)
    if "Year" not in sum_dims:
        raise TypeError("'Year' dimension not found in array data")

    # Define the cumsum and sum dimentions and check for one element dimensions
    sum_dims.remove("Year")
    if ax is None:
        f, ax = plt.subplots(1, **kwargs)

    if show in sum_dims:
        sum_dims.remove(show)
        size_cumsum = food.sizes[show]
        if stack:
            cumsum = food.cumsum(dim=show).transpose(show, ...)
        else:
            cumsum = food
    else:
        size_cumsum = 1
        cumsum = food

    # Collapse remaining dimensions
    cumsum = cumsum.sum(dim=sum_dims)
    years = food.Year.values

    # If colors are not defined, generate a list from the standard cycling
    if colors is None:
        colors = [f"C{ic}" for ic in range(size_cumsum)]

    # Plot
    if size_cumsum == 1:
        ax.fill_between(years, cumsum, color=colors[0], alpha=0.5)
        ax.plot(years, cumsum, color=colors[0], linewidth=0.5, label=label)
    else:
        for id in reversed(range(size_cumsum)):
            ax.fill_between(years, cumsum[id], color=colors[id], alpha=0.5)
            ax.plot(years, cumsum[id], color=colors[id], linewidth=0.5,
                    label=label[id])

    ax.set_xlim(years.min(), years.max())
    ax.set_ylim(bottom=0)

    if label is not None:
        ax.legend()

    return ax

def plot_map(map, ax=None, **kwargs):

    if ax is None:
        f, ax = plt.subplots(1)

    # Get plot ranges
    xmin, xmax = map.x.values[[0, -1]]
    ymin, ymax = map.y.values[[0, -1]]

    ax.imshow(map, interpolation="none", origin="lower",
              extent=[xmin, xmax, ymin, ymax])
    
    return ax