"""Module for creating tables"""

from pathlib import Path

import pandas as pd

from py.models.member_stats import MemberStats
from py.models.message_superlative import MessageSuperlative
from py.models.chat_stats import ChatStats


def popular_message_table(messages: list[MessageSuperlative], output_file: Path):
    """Create table with most popular messages"""
    headers = list(MessageSuperlative.model_fields.keys())
    messages_ranked = pd.DataFrame(columns=headers, index=range(len(messages)))
    for i, message in enumerate(messages):
        messages_ranked.iloc[i] = list(message.model_dump().values())
    messages_ranked.to_csv(output_file, sep=",", encoding="utf-8", index=False)


def chat_summary_table(chat_stats: ChatStats, output_file: Path):
    """Create table with most popular messages"""
    headers = ["Stat", "Value"]
    chat_summary = pd.DataFrame(
        columns=headers, index=range(len(ChatStats.model_fields.keys()))
    )
    stats = list(chat_stats.model_dump().values())
    for i, name in enumerate(chat_stats.model_fields.keys()):
        chat_summary.iloc[i] = [name, stats[i]]
    chat_summary.to_csv(output_file, sep=",", encoding="utf-8", index=False)


def member_summary_table(
    member_stats: dict[str, MemberStats],
    keyword_map: dict[str, dict[str, int]],
    output_file: Path,
):
    """Create a table with summary stats for each player"""
    headers = [
        "Member",
        "Messages Sent",
        "Average Word Count",
        "Reactions Received",
        "Reactions Given",
        "Likes Recieved",
        "Likes Given",
        "Dislikes Received",
        "Dislikes Given",
        "Biggest Fan",
        "Biggest Supporter Of",
        "Avg Likes Per Post",
        "Most Active Day",
        "Most Active Hour",
        "Images Sent",
        "Polls Made",
    ]
    for key in keyword_map.keys():
        headers += [key]
    summary = pd.DataFrame(columns=headers, index=range(len(member_stats.keys())))
    for i, (name, stats) in enumerate(member_stats.items()):

        keywords_append = [members[name] for members in keyword_map.values()]
        summary.iloc[i] = [
            name,
            stats.messages_sent,
            stats.average_word_count,
            stats.reactions_received,
            stats.reactions_given,
            stats.hearts_received,
            stats.hearts_given,
            stats.dislikes_received,
            stats.dislikes_given,
            stats.biggest_fan,
            stats.biggest_supporter_of,
            stats.heart_message_ratio,
            stats.most_active_day,
            stats.most_active_hour,
            stats.images_sent,
            stats.polls_made,
        ] + keywords_append
    summary.to_csv(output_file, sep=",", encoding="utf-8", index=False)
