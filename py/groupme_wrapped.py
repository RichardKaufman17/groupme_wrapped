"""Executable to perform GroupMe wrapped"""

import logging

import typer
from typing_extensions import Annotated

from py.utils.logger import initialize_logger
from py.utils.utility import validate_json_input
from py.utils.directories import FileData
from py.groupme_api.fetch_chat import FetchChat
from py.models.analysis_config import read_analysis_config
from py.data_processing.analysis import Analysis

LOG = logging.getLogger(__name__)


def main(
    chat_json: Annotated[str, typer.Option(help="Name of json file to save chat to")],
    download_chat: Annotated[
        bool, typer.Option(help="Whether to download chat data")
    ] = False,
    chat_id: Annotated[str | None, typer.Option(help="Chat ID number")] = None,
    access_token: Annotated[
        str | None, typer.Option(help="GroupMe API access token")
    ] = None,
    analysis_config: Annotated[
        str | None, typer.Option(help="json file with analysis parameters")
    ] = None,
    log_level: Annotated[
        str, typer.Option(help="Level to log (INFO, DEBUG, ERROR)")
    ] = "INFO",
):
    """Main execution of GroupMe Wrapped"""
    try:

        # Initialize Logging
        initialize_logger(log_level)

        # Initialize chat output
        json_outout = validate_json_input(chat_json)
        chat_path = FileData.raw_output_dir / json_outout

        # Parameters for chat data analysis
        config = read_analysis_config(analysis_config)

        # Download chat data
        if download_chat:
            assert (
                access_token is not None
            ), "Must input access token to fetch groupme data"
            assert chat_id is not None, "Must input chat id to fetch groupme data"
            FetchChat(
                chat_id=chat_id,
                acces_token=access_token,
                output_file=chat_path,
                config=config,
            ).fetch_chat()

        # Analyze chat data
        Analysis(config, chat_path).analyze_chat()

    except Exception as e:  # pylint: disable=broad-exception-caught
        LOG.error(e)
        raise


if __name__ == "__main__":
    typer.run(main)
