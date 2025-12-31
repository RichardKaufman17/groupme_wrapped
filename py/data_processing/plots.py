"""Module for to create plots for analysis"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns  # type: ignore


def reaction_heat_map(
    reaction_dict: dict[str, dict[str, int]], plot_title: str, output_file: Path
):
    """Create heat map of feactions"""

    member_received = list(reaction_dict.keys()) + ["Total reactions given"]
    member_given = list(reaction_dict.keys()) + ["Total reactions received"]

    # Fill numpy 2D array
    reaction_table = np.zeros(
        shape=(len(member_received), len(member_given)), dtype=int
    )
    for receiver, reactions in reaction_dict.items():
        for reacter, total in reactions.items():
            reaction_table[member_received.index(receiver)][
                member_received.index(reacter)
            ] = total
    total_table = np.zeros(shape=(len(member_received), len(member_given)), dtype=int)
    total_table[-1] = np.sum(reaction_table, axis=0)
    total_table[:, -1] = np.sum(reaction_table, axis=1)
    _, ax = plt.subplots(figsize=(14, 10))

    sns.heatmap(
        data=reaction_table,
        annot=True,
        ax=ax,
        cmap=sns.color_palette("rocket_r", as_cmap=True),
        fmt="g",
        xticklabels=True,
        yticklabels=True,
        mask=total_table,
    )
    sns.heatmap(
        data=total_table,
        annot=True,
        ax=ax,
        cmap="Blues",
        fmt="g",
        mask=reaction_table,
    )
    ax.collections[0].colorbar.set_label(  # type: ignore
        "Number of Reactions (per user)", fontsize=15
    )
    ax.collections[1].colorbar.set_label(  # type: ignore
        "Number of Reactions (totals)", fontsize=15
    )
    ax.set_xticklabels(member_given, rotation=45, ha="right", rotation_mode="anchor")
    ax.set_yticklabels(member_received, rotation=0, ha="right", rotation_mode="anchor")
    ax.tick_params(axis="both", labelsize=10)
    ax.set_title(plot_title, fontsize=20)
    ax.set_ylabel("Reactions received by member", fontsize=15)
    ax.set_xlabel("Reactions given by member", fontsize=15)
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()


def histograms(
    dataset: int, labels: list[str], title: str, x_label: str, output_file: Path
):
    """Create a histogram from integers in `dataset`"""
    _, ax = plt.subplots(figsize=(14, 10))
    bins = np.arange(start=-0.5, stop=len(labels) + 0.5, step=1)
    bin_ticks = bins[:-1] + 0.5
    ax.hist(
        dataset,
        bins=list(bins),
        edgecolor="black",
        color="blue",
        alpha=0.6,
        align="mid",
    )
    ax.set_title(title, fontsize=20)
    ax.set_xlabel(x_label, fontsize=15)
    ax.set_ylabel("Number of messages", fontsize=15)
    ax.set_xticks(
        ticks=bin_ticks, labels=labels, rotation=45, ha="right", rotation_mode="anchor"
    )
    ax.tick_params(axis="both", labelsize=10)
    ax.set_xlim(-0.5, len(labels) - 0.5)

    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()


def plot_superlatives(
    data: dict[str, float], title: str, y_label: str, output_file: str
):
    """Rank group chat members by superlative scores"""

    data = {
        k: v for k, v in sorted(data.items(), key=lambda item: item[1], reverse=True)
    }
    _, ax = plt.subplots(figsize=(14, 10))
    ax.bar(
        list(range(len(data.values()))),
        list(data.values()),
        align="center",
        alpha=0.6,
        edgecolor="black",
        color="blue",
    )
    ax.set_title(title, fontsize=20)
    ax.set_xlabel("Members", fontsize=15)
    ax.set_ylabel(y_label, fontsize=15)
    ax.set_xticks(
        ticks=list(range(len(data.values()))),
        labels=list(data.keys()),
        rotation=45,
        ha="right",
        rotation_mode="anchor",
    )
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()


def plot_keyword_occurances(keyword_map: dict[str, dict[str, int]], output_file: Path):
    """Plot occurances of keywords, by member, defined in `keyword_map` to `outout_file`"""

    _, ax = plt.subplots(figsize=(14, 10))

    labels: list[str] = []
    bar_layers: dict[str, list[int]] = {
        member: [] for member in next(iter(keyword_map.values())).keys()
    }
    for key, value in keyword_map.items():
        labels += [key]
        for member, count in value.items():
            bar_layers[member] += [count]

    bottoms = len(labels) * [0]
    for member, counts in bar_layers.items():
        ax.bar(labels, counts, label=member, bottom=bottoms, edgecolor="black")
        bottoms = [bottom + count for bottom, count in zip(bottoms, counts)]

    ax.set_ylim(0, max(bottoms))
    ax.set_title("Common Groupchat Words and Phrases", fontsize=20)
    ax.set_xlabel("Word / Phrase", fontsize=15)
    ax.set_ylabel("Number of Messages that Include Word / Phrase", fontsize=15)
    ax.legend(loc="upper right")

    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()
