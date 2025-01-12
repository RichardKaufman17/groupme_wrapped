"""Module for groupme chat analysis"""

import json
import logging
from pathlib import Path
from datetime import datetime

from py.models.analysis_config import AnalysisConfig
from py.models.message_template import ChatMessage
from py.utils.utility import remove_unicode_characters
from py.models.message_template import AttachmentType, ReactionEmojis
from py.models.member_stats import MemberStats, HOURS, DAYS
from py.models.message_superlative import MessageSuperlative
from py.models.chat_stats import ChatStats
from py.data_processing.plots import (
    reaction_heat_map,
    histograms,
    plot_superlatives,
    plot_keyword_occurances,
)
from py.data_processing.tables import (
    member_summary_table,
    popular_message_table,
    chat_summary_table,
)
from py.utils.directories import FileData

LOG = logging.getLogger(__name__)

GROUPME_NAMES = ["system", "calendar"]


class Analysis:
    """Class to handle analaysis of GroupMe chat data"""

    def __init__(
        self, analysis_config: AnalysisConfig, chat_path: Path, results_dir: Path
    ):
        self.config = analysis_config
        self.chat_path = chat_path
        self.output_dir = results_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Read chat
        self.messages = self.read_chat_json()

        # Member Names
        self.id_to_names: dict[str, list[str]] = {}
        self.id_to_name: dict[str, str] = {}
        self.chat_member_names: list[str] = []
        self.map_id_to_name()
        self.process_member_names()

        # Results
        self.chat_stats = ChatStats()
        self.keyword_map: dict[str, dict[str, int]] = {}
        self.member_stats: dict[str, MemberStats] = {}
        self.initialize_results_dicts()
        self.best_messages: list[MessageSuperlative] = []

    def analyze_chat(self):
        """Method to run all chat analyses"""
        self.get_member_stats()
        self.calculate_superlatives()
        self.reaction_heat_maps()
        self.time_distribution()
        self.member_summary()
        self.chat_summary()
        self.keyword_plots()
        self.most_popular_messages()

    def map_id_to_name(self):
        """Map user id numbers to member names"""

        for message in self.messages:
            try:
                if message.name not in self.id_to_names[message.user_id]:
                    self.id_to_names[message.user_id] += [message.name]
            except KeyError:
                if message.user_id not in GROUPME_NAMES:
                    self.id_to_names[message.user_id] = [message.name]

    def process_member_names(self):
        """Use most recent name of each member and remove unicode characters"""
        self.id_to_name = {
            key: remove_unicode_characters(value[0])
            for key, value in self.id_to_names.items()
        }
        for name in self.id_to_name.values():
            self.chat_member_names += [name]

    def read_chat_json(self) -> list[ChatMessage]:
        """Read chat messages from json file"""
        LOG.info("Reading chat from %s", self.chat_path)
        with open(self.chat_path, encoding="utf-8") as json_file:
            messages = json.load(json_file)

            return [
                ChatMessage.model_validate_json(json.dumps(message))
                for message in messages
            ]

    def initialize_results_dicts(self):
        """Initialize results dictionaries"""
        # Results
        for name in self.chat_member_names:
            self.member_stats[name] = MemberStats()
            self.member_stats[name].initialize_dicts(self.chat_member_names)
        if self.config.chat_keywords is not None:
            for keyword in self.config.chat_keywords:
                self.keyword_map[keyword.name] = {}
                for member in self.chat_member_names:
                    self.keyword_map[keyword.name][member] = 0

    def get_member_stats(self):
        """Get stats for each group chat member, populate fields in `MemberStats` class"""

        # Loop through each message
        for message in self.messages:
            try:
                poster = self.id_to_name[message.user_id]
                self.increment_vals(poster, message)
                self.add_stats_for_reaction(poster, message)
                self.add_stats_for_like_and_dislike(poster, message)
                if self.config.chat_keywords is not None:
                    self.keyword_increment(poster, message)
                self.update_message_superlative(poster, message)
            except KeyError:
                # Ignore posts made by groupme bots
                continue

    def update_message_superlative(self, poster: str, message: ChatMessage):
        """Update the message superlative list with `message`"""
        if message.reactions is None:
            return
        total_likes = 0
        likers: list[str] = []
        image_attachment: str | None = None
        for reaction in message.reactions:
            if reaction.code in [
                ReactionEmojis.HEART.value,
                ReactionEmojis.LIKE.value,
            ]:
                total_likes += len(reaction.user_ids)
                likers += [self.id_to_name[name] for name in reaction.user_ids]
        for attachment in message.attachments:
            if attachment.type == AttachmentType.IMAGE:
                image_attachment = attachment.url
                break
        text = (
            message.text
            if message.text is None
            else remove_unicode_characters(message.text)
        )
        new_message = MessageSuperlative(
            poster=poster,
            created_at=datetime.fromtimestamp(message.created_at),
            text=text,
            image_attachment=image_attachment,
            likers=likers,
            total_likes=len(likers),
        )
        for i, top_message in enumerate(self.best_messages):
            if total_likes > top_message.total_likes:
                self.best_messages.insert(i, new_message)
                self.best_messages = self.best_messages[:-1]
                break
        if (
            len(self.best_messages) < self.config.num_messages_rank
            and new_message not in self.best_messages
        ):
            self.best_messages += [new_message]

    def keyword_increment(self, poster: str, message: ChatMessage):
        """Increment the number of times a keyword occurs"""
        keywords = self.config.chat_keywords
        assert keywords is not None, "No keywords specified in config file"

        for keyword in keywords:
            for alias in keyword.aliases:
                if message.text is not None and alias in message.text.lower():
                    self.keyword_map[keyword.name][poster] += 1
                    break

    def increment_vals(self, poster: str, message: ChatMessage):
        """Increment stat values from message"""
        # Increment Message
        self.member_stats[poster].messages_sent += 1
        self.chat_stats.num_messages += 1

        # Increment Attachments
        for attachment in message.attachments:
            if attachment.type == AttachmentType.POLL:
                self.member_stats[poster].polls_made += 1
                self.chat_stats.total_polls += 1
            elif attachment.type == AttachmentType.IMAGE:
                self.member_stats[poster].images_sent += 1
                self.chat_stats.total_image_attachments += 1

        # Word Count
        if message.text is not None:
            self.member_stats[poster].word_count += len(message.text.split(" "))
            self.chat_stats.average_word_count += len(message.text.split(" "))

        # Time posted
        date_posted = datetime.fromtimestamp(message.created_at)
        self.member_stats[poster].hours_posted += [date_posted.hour]
        self.member_stats[poster].days_posted += [date_posted.weekday()]

    def add_stats_for_reaction(self, poster: str, message: ChatMessage):
        """Add stats for reactions"""

        self.member_stats[poster].reactions_received += len(message.favorited_by)
        self.chat_stats.total_reactions += len(message.favorited_by)
        for reacter in message.favorited_by:
            reacter = self.id_to_name[reacter]
            self.member_stats[reacter].reactions_given += 1
            self.member_stats[poster].reactions_received_by_sender[reacter] += 1

    def add_stats_for_like_and_dislike(self, poster: str, message: ChatMessage):
        """Add stats for likes and dislikes"""

        if message.reactions is not None:
            for reaction in message.reactions:
                if reaction.code in [
                    ReactionEmojis.HEART.value,
                    ReactionEmojis.LIKE.value,
                ]:
                    self.member_stats[poster].hearts_received += len(reaction.user_ids)
                    self.chat_stats.total_likes += len(reaction.user_ids)
                    for reacter in reaction.user_ids:
                        reacter = self.id_to_name[reacter]
                        self.member_stats[reacter].hearts_given += 1
                        self.member_stats[poster].hearts_received_by_sender[
                            reacter
                        ] += 1
                        self.member_stats[reacter].hearts_given_by_receiver[poster] += 1
                elif reaction.code in [
                    ReactionEmojis.DISLIKE.value,
                    ReactionEmojis.QUESTION.value,
                ]:
                    self.member_stats[poster].dislikes_received += 1
                    self.chat_stats.total_dislikes += len(reaction.user_ids)
                    for reacter in reaction.user_ids:
                        reacter = self.id_to_name[reacter]
                        self.member_stats[poster].dislikes_received_by_sender[
                            reacter
                        ] += 1
                        self.member_stats[reacter].dislikes_given += 1

    def calculate_superlatives(self):
        """Calculate surperaltives from member stats"""
        LOG.info("Calculating and plotting chat superlatives")
        self.chat_stats.average_word_count = (
            self.chat_stats.average_word_count / self.chat_stats.num_messages
        )
        for member in self.member_stats.values():
            member.post_time_modes()
            member.get_verbosity()
            member.get_reaction_superlatives()

        superlative_dir = self.output_dir / FileData.superlative_folder
        superlative_dir.mkdir(exist_ok=True)

        # Ranked by Number of messages
        superlative = {
            name: member.messages_sent for name, member in self.member_stats.items()
        }
        plot_superlatives(
            superlative,
            f"{self.config.chat_name}: Messages Posted by User",
            "Number of messages",
            superlative_dir / FileData.ranked_by_message,
        )

        # Ranked by likes per message
        superlative = {
            name: member.heart_message_ratio
            for name, member in self.member_stats.items()
        }
        plot_superlatives(
            superlative,
            f"{self.config.chat_name}: Average Likes per post",
            "Like / Post ratio",
            superlative_dir / FileData.like_pos_ratio,
        )

        # Ranked by Number of messages
        superlative = {
            name: member.average_word_count
            for name, member in self.member_stats.items()
        }
        plot_superlatives(
            superlative,
            f"{self.config.chat_name}: Average Word Count, by Member",
            "Word Count",
            superlative_dir / FileData.word_count,
        )

        # Ranked by image attachments
        superlative = {
            name: member.images_sent for name, member in self.member_stats.items()
        }
        plot_superlatives(
            superlative,
            f"{self.config.chat_name}: Number of Images Posted, by Member",
            "Image Attachments",
            superlative_dir / FileData.images_ranked,
        )

        # Ranked by polls made
        superlative = {
            name: member.polls_made for name, member in self.member_stats.items()
        }
        plot_superlatives(
            superlative,
            f"{self.config.chat_name}: Number of Polls Made, by Member",
            "Polls",
            superlative_dir / FileData.polls_ranked,
        )

    def member_summary(self):
        """Create a summary table of chat data"""
        LOG.info("Creating Member Summary Table")
        summary_file = self.output_dir / FileData.member_summary
        member_summary_table(self.member_stats, self.keyword_map, summary_file)

    def most_popular_messages(self):
        """Create a table with the most popular messages"""
        LOG.info("Create a table of the most popular messages")
        output_file = self.output_dir / FileData.popular_messages
        popular_message_table(self.best_messages, output_file)

    def time_distribution(self):
        """Create histograms for monthly and yearly posts"""
        LOG.info("Calculating and plotting chat activity")
        histogram_dir = self.output_dir / "post_frequency"
        histogram_dir.mkdir(exist_ok=True)

        all_hours = []
        all_days = []
        for name, member in self.member_stats.items():
            histograms(
                member.hours_posted,
                HOURS,
                f"{name}'s Daily Post Distribution",
                "Hour",
                histogram_dir / f"{name}{FileData.daily}",
            )
            histograms(
                member.days_posted,
                DAYS,
                f"{name} Weekly Post Distribution",
                "Day of Week",
                histogram_dir / f"{name}{FileData.weekly}",
            )
            all_hours += member.hours_posted
            all_days += member.days_posted
        # Histogram for all posts in chat
        histograms(
            all_hours,
            HOURS,
            f"{self.config.chat_name}'s Daily Post Distribution",
            "Hour",
            histogram_dir / f"{self.config.chat_name}{FileData.daily}",
        )
        histograms(
            all_days,
            DAYS,
            f"{self.config.chat_name}'s Weekly Post Distribution",
            "Day of Week",
            histogram_dir / f"{self.config.chat_name}{FileData.weekly}",
        )

    def reaction_heat_maps(self):
        """Create heat maps for reactions"""
        LOG.info("Calculating and plotting chat reactions")
        heatmap_dir = self.output_dir / FileData.heatmap_folder
        heatmap_dir.mkdir(exist_ok=True)
        # Heat map for all reactions
        reaction_dict = {
            name: stats.reactions_received_by_sender
            for name, stats in self.member_stats.items()
        }
        reaction_map_output = heatmap_dir / FileData.reaction_heatmap
        title = f"{self.config.chat_name} Reactions by Member"
        reaction_heat_map(reaction_dict, title, reaction_map_output)

        # Heat map for heart reactions
        reaction_dict = {
            name: stats.hearts_received_by_sender
            for name, stats in self.member_stats.items()
        }
        reaction_map_output = heatmap_dir / FileData.hearts_heatmap
        title = f"{self.config.chat_name} Hearts by Member"
        reaction_heat_map(reaction_dict, title, reaction_map_output)

        # Heat map for dislike
        reaction_dict = {
            name: stats.dislikes_received_by_sender
            for name, stats in self.member_stats.items()
        }
        reaction_map_output = heatmap_dir / FileData.dislikes_heatmap
        title = f"{self.config.chat_name} Dislikes by Member"
        reaction_heat_map(reaction_dict, title, reaction_map_output)

    def keyword_plots(self):
        """Plot how frequently each keyword appeared"""
        LOG.info("Create bar chat for popular chat words and phrases")
        output_file = self.output_dir / FileData.chat_keywords
        plot_keyword_occurances(self.keyword_map, output_file)

    def chat_summary(self):
        """Create table with chat summary data"""
        LOG.info("Creating Chat Summary Table")
        output_file = self.output_dir / FileData.chat_summary
        chat_summary_table(self.chat_stats, output_file)
