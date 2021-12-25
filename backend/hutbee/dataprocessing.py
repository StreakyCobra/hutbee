# -*- coding: utf-8 -*-
"""Hutbee data processing."""

import io
from datetime import datetime, timedelta

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib import ticker
from matplotlib.dates import HourLocator
from pymongo import MongoClient
from pymongo.cursor import Cursor

from hutbee.config import DISPLAY_TIMEZONE
from hutbee.db import DB


def history_plot(cursor: Cursor) -> io.BytesIO:
    # Read and prepare the data
    data = pd.DataFrame(
        [
            {
                "date": datetime.fromisoformat(v["date"]),
                "temperature": v["values"]["temperature"],
                "co2": v["values"]["co2"],
                "humidity": v["values"]["humidity"],
            }
            for v in cursor
            if v["values"] is not None
        ]
    )
    data = data.sort_values(["date"])
    data = data.set_index("date")
    data = data.resample("10 min").mean()
    data = data.reset_index()

    # Create a figure
    fig = plt.Figure(figsize=(8, 8))

    # Define the colors
    colors = sns.color_palette()

    # Prepare the axes
    axes = fig.subplots(
        gridspec_kw={"height_ratios": [4, 2, 1]},
        nrows=3,
        ncols=1,
        sharex=True,
    )
    ax1, ax2, ax3 = axes

    # Plot the data
    sns.lineplot(
        data=data,
        x="date",
        y="temperature",
        label="Temperature",
        color=colors[0],
        ax=ax1,
    )
    sns.lineplot(
        data=data,
        x="date",
        y="co2",
        label="CO₂",
        color=colors[1],
        ax=ax2,
    )
    sns.lineplot(
        data=data,
        x="date",
        y="humidity",
        label="Humidity",
        color=colors[2],
        ax=ax3,
    )

    # X ticks
    ax3.xaxis.set_minor_locator(HourLocator(interval=1))
    ax3.xaxis.set_major_locator(HourLocator(interval=3))
    ax3.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=DISPLAY_TIMEZONE))
    for item in ax3.get_xticklabels():
        item.set_rotation(90)

    # Y ticks
    ax1.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x} °C"))
    ax2.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:.0f} ppm"))
    ax3.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x} %"))

    # Grids
    for ax in axes:
        ax.grid(which="major")
        ax.grid(which="minor", linestyle=":", linewidth="0.4", color="#aaa")

    # Axes labels
    for ax in axes:
        ax.set_ylabel("")
    ax3.set_xlabel("")

    # Legend
    lns = [l for ax in axes for l in ax.lines]
    labs = [l.get_label() for l in lns]
    ax1.legend(lns, labs, loc=1)
    ax2.legend().remove()
    ax3.legend().remove()

    # CO₂ indications
    lim2 = ax2.get_ylim()
    ax2.axhspan(0, 1000, color="green", alpha=0.1)
    ax2.axhspan(1000, 2000, color="orange", alpha=0.1)
    ax2.axhspan(2000, 5000, color="red", alpha=0.1)
    ax2.set_ylim(lim2)

    # Save the figure in memory
    img = io.BytesIO()
    fig.tight_layout()
    fig.savefig(img, format="png")
    img.seek(0)

    # Return the image
    return img
