"""Store on directory paths and filenames"""

from dataclasses import dataclass
from pathlib import Path

PY_PATH: Path = Path(__file__).parents[2]

@dataclass
class FileData:
    """Contains directories and filenames"""

    # Directories
    raw_output_dir: Path = PY_PATH / "raw_outputs"
    log_dir: Path = PY_PATH / "logs"
    analysis_configs: Path = PY_PATH / "analysis_configs"
    results_dir: Path = PY_PATH / "output_figures"

    # Heatmap results
    heatmap_folder: str = "reaction_heatmaps"
    reaction_heatmap: str = "reaction_heatmap.png"
    hearts_heatmap: str = "hearts_heatmap.png"
    dislikes_heatmap: str = "dislikes_heatmap.png"

    # Superlatives
    superlative_folder: str = "superlatives"
    ranked_by_message: str = "ranked_by_messages.png"
    like_pos_ratio: str = "like_post_ratio.png"
    word_count: str = "word_count_ranked.png"
    images_ranked: str = "images_ranked.png"
    polls_ranked: str = "polls_ranked.png"

    # Chat keywords
    chat_keywords: str = "chat_keywords.png"

    # Tables
    popular_messages: str = "most_popular_messages.csv"
    member_summary: str = "member_summary.csv"
    chat_summary: str = "chat_summary.csv"

    # Chat Activity
    daily: str = "_daily_post_distribution"
    weekly: str = "_weekly_post_distribution"
