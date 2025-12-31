# GroupMe Wrapped: GroupMe Chat Analysis

## Contents

* [Background](#background)
* [Prerequisites](#prerequisites)
    * [Installation](#installations)
        * [Python Install](#python-install) 
        * [Poetry Install](#poetry-install)
    * [GroupMe API](#groupme-api)
        * [Chat ID](#chat-id)
        * [Access Token](#access-token)
    * [Virtual Environment Setup](#virtual-environment-setup)
        * [Set up environment and install dependencies](#set-up-environment-and-install-dependencies)
        * [Optional: Develop in environment with Visual Studio Code ID](#optional-develop-in-environment-with-visual-studio-code-ide)
* [Analysis Config File](#analysis-config-file)
* [Execution](#execution)
* [Outputs](#outputs)
    * [Chat Stats](#chat-stats)
    * [Member Superlatives](#member-superlatives)
    * [Reaction Heatmaps](#reaction-heatmaps)
    * [Member Summary](#member-summary)
    * [Popular Messages](#popular-messages)
    * [Chat Keywords](#chat-keywords)
    * [Chat Activity](#chat-activity)
    * [Logs](#logs)

## Background

Inspired by the "wrapped" and "year in review" content that many products offer now, this program provides an easy way for friends to analyze the messages and activity in their GroupMe groupchat. 

Utilizing GroupMe's API, this script will fetch all chat messages within a user-specified time range and output fun statistics outlining the highlights of each member's groupchat activity.

## Prerequisites

### Installations

There are two prequisites that must be installed to run this program:

1. python 3.12+
2. poetry

#### Python install:

[Install python 3.12](https://www.python.org/downloads/)

#### Poetry install

Install poetry by running the following commands in terminal:

* `pip install pipx`
* `pipx install poetry`

### GroupMe API

In order to run the script, you will need:
* The groupchat ID number
* Your GroupMe account access token

#### Chat ID

1. Log into GroupMe and open the chat you would like to analyze
2. Go to group settings
3. Enable group sharing
4. Grab the chat-id number from the group sharing link *https://groupme.com/join_group/\<id\>/*

![group_id](/docs/group_id.png)

Notes:
* User must be an admin of the chat to enable group sharing
* Sharing can be disabled again after grabbing the ID number. It is not necessary for the script

#### Access Token

1. Navigate to the [GroupMe API page](https://dev.groupme.com/)
2. Log into your GroupMe account
3. Select *Access Token* on the top right menu bar and copy your access token
![access_token](/docs/access_token.png)

## Virtual Environment Setup

### Set up environment and install dependencies

The GroupMe Wrapped script requires several packages not included in the Python standard library. [Poetry](https://python-poetry.org/) is used as a virtual environment for dependency management. Ensure that [python 3.12 and poetry](#prerequisites) are installed before proceeding with this step. 

1. Open a new terminal (linux) or Windows Power Shell
2. Navigate to the directory of this repo `cd <path>/groupme_wrapped`
3. Execute the command `poetry install`

Python scipts may now be executed
* in the current shell
    * `poetry run python <filename>.py`
* within poetry shell
    * `poetry shell`
    * `python <filename>.py`

### Optional: Develop in environment with Visual Studio Code IDE

In order for your IDE to recognize the virtual environment you are working in, in this case, `groupme_wrapped`, ensure the correct python interpreter is selected. The interpreter path for the virtual environment creaed with poetry can be found by running:
* `poetry env info`

The interpreter path will be printed to terminal

If using Visual Studio Code, perform the following in order to get the IDE to recognize the environment and its dependencies, once vs code is opened:
* Enter `crtl+shift+p`
* Type and Enter: `python: select interpreter`
* Select option: `Select at the Workplace Level`
* Select `Enter Interpreter Path`
* Paste the path copied from running `poetry env info`

## Analysis Config File

The script reads a json file located in [analysis_configs](./analysis_configs/) with instructions on how to collect and analyze the chat data. This file must be included in order to run the GroupMe wrapped script. 

The json file should follow the format defined in [analysis_config.py](./py/models/analysis_config.py), such as this [template](./docs/config_example.json):

```
{
    "message_request_limit": 200,
    "start_date": "2024-01-01",
    "end_date": "2025-01-01",
    "chat_name": "Group",
    "chat_keywords":
    [
        {
            "name": "twitter",
            "aliases": ["twitter", "tweet", "x.com"]
        },
        {
            "name": "meme",
            "aliases": ["meme"]
        }
    ],
    "num_messages_rank": 10
}
```

The following data can be included in the config file:

| parameter | datatype |default | description | 
| --------- | -------- | ------ | ----------- |
| message_request_limit | int | 200 | Amount of messages to grab in a single request |
| chat_name | str | "Group Chat" | Name of groupchat to be referred to in figures | 
| output_folder | str | `chat_name` | Folder to save output data |
| start_date | Optional[Union[datetime, int]] | None | default start date of messages to analyze, as datetime (%Y-%m-%d %H:%M:%S) or timestamp. When set to none, all messages sent before `end_date` will be fetched |
| end_date | Optional[Union[datetime, int]] | None | default end date of messages to analyze, as datetime (%Y-%m-%d %H:%M:%S) or timestamp. When set to none, all messages sent after `start_date` will be fetched |
| num_messages_rank | int | 10 | The top `num_messages_rank` messages (top *n* messages with the most likes) will be listed in [most_popular_messages.csv](#popular-messages)
| chat_keywords | Optional[list[`ChatKeywords`]] | None | A list of chat keywords to analyze. Each element of the list is an instance of the `ChatKeywords` class. A [bar chart](#chat-keywords) will be made displaying the number of times each keyword was said, categorized by poster.

Under `chat_keywords`, define a list of dictionaries with the following keys:
| parameter | datatype | description | 
| --------- | -------- | ----------- |
| name | str | the primary name of the keyword, which will appear on the tick labels |
| aliases | list[str] | A list of all strings which will count towards a use of the keyword. A message is counted if any of the aliases are used |


## Execution

To execute the GroupMe Wrapped script, enter the directory [groupme_wrapped/py](/py/) in terminal and enter the following command:

`poetry run python groupme_wrapped.py --analysis-config <confg-file> --chat-json <name-to-save-chat> --download-chat --access-token <access_token> --chat-id <chat_id> --log-level <log_level>`

For details on each argument, run the script with the `--help` argument:

`poetry run python groupme_wrapped.py --help`

The table below summarizes each input argument

| parameter | Optional | description | notes |
| --------- | -------- | ----------- | ----- |
| --download-chat | Yes | Groupme messages will be fetched when this argument is added. | If not added, the script will skip straight to analysis. |
| --chat-json | No | The name of the json file that the chat data will be saved to. If chat data is not fetched, the script will search for an existing json file with this name to analyze | If no file extension is given, a `.json` will be appended to the end of the argument string |
| --access-token | Yes | The [access token](#access-token) of the chat to fetch | Not required if the `--download-chat` argument is not included |
| --chat-id | Yes | The [chat id](#chat-id) of the chat to fetch | Not required if the `--download-chat` argument is not included |
| --analysis-config | No | The filename of the [analysis config json file](#analysis-config-file) | If no file extension is given, a `.json` will be appended to the end of the argument string. If no config is specified, the [default](./py/models/analysis_config.py) will be used. |
| --log-level | Yes | The log level of script [log messages](#logs) to save | Defaults to "info". Options include, in hierarchal order, "debug", "info", "warning" and "error" |

Below is an example of a script execution and arguments:

`poetry run python groupme_wrapped.py --download-chat --analysis-config config_file.json --access-token 23498y23bwre --chat-id 909234 --chat-json groupchat_messages`

In the above example, chat messages belonging to `chat_id` will be fetched. The dates to grab the data, and the number of messages per request, are specified in `config_file.json`. The chat messages will be saved to `groupchat_messages.json`.

## Outputs

### Chat Stats

General chat statistics will be output to a csv *groupme_wrapped/output_figures/chat_summary.csv*

This csv will include the following data:
* Number of messages
* Average word count
* Total reactions
* Total likes
* Total dislikes
* Total images sent
* Total polls made

### Member Superlatives

Member superlative plots are saved to *groupme_wrapped/output_figures/superlatives*. Each plot is a bar chart where each bar represents an individual chat member and the y-value indicates the quantity. The following categories are plotted
* Images sent
* Average likes per post
* Average word count
* Number of polls made
* Number of messages sent

Below is an example of a superlative chart for number of messages sent. It ranks each member by the number of messages sent to the chat within the timeframe that was fetched for anlaysis. 

![ranked](/docs/ranked_by_messages.png)

### Reaction Heatmaps

A reaction heatmap displays how many reactions each user received from each other user. Three reaction heatmaps are generated in total:
* All reactions
* Just likes (likes and hearts)
* Just dislikes (dislike and question reacts)

Reaction heatmaps will be saved to the directory *groupme_wrapped/output_figures/reaction_heatmaps/*

Below is an example of a heatmap for all reactions:
![heatmap](/docs/reaction_heatmap.png)

In the above example, we see that Anthony received 195 reactions from Tristan. Moreover, we can also conclude from the same cell that Tristan gave Anthony 195 reactions.

### Member Summary

The member summary is an output csv with summarized data for each chat member. It is saved to *groupme_wrapped/output_figures/member_summary.csv*. For each member, it will list:
* Number of messages sent
* Average word count
* Number of reactions received
* Number of reactions given
* Number of likes received
* Number of likes given
* Number of dislikes received
* Number of dislikes given
* Biggest fan
* Biggest supporter of
* Average likes per message
* Most active day of the week
* Most active hour of the day
* Number of messages where each [keyword](#chat-keywords) was included

### Popular Messages

A csv listing the N most popular (most likes + hearts) messages is saved to *groupme_wrapped/output_figures/most_popular_messages.csv*. N is the number specified in the [analysis_config.json](#analysis-config-file) file, under the field `num_messages_ranked`.

For each message listed in the csv file, data will include:
* Message text
* Number of likes the message received
* List of members who liked the message
* A url to an image attachment, if included

### Chat Keywords

Special chat keywords to track can be specified in the [analysis_config.json](#analysis-config-file) with the `chat_keywords` field. A bar chart is created to exhibit the number of messages where any of the aliases of each keyword were used. Each bar is split into subsections of different colors representing the number of messages each individual member sent that used the word. The barchart is saved to *groupme_wrapped/output_figures/chat_keywords.png*.

Below is an example with mentions of prominant politicans:

![keywords](/docs/chat_keywords.png)

### Chat Activity

Daily and weekly chat activity is plotted for the chat at large and for each individual member. Both daily and weekly chat activity is depicted through a histogram where the Y-axis is the number of messages sent. The x-axis includes:
* Weekly case: 7 bins for each day of the week
* daily case: 24 bins for each hour of the day

All chat activity plots are saved under the directory *groupme_wrapped/output_figures/post_frequency/*

Below is an example of the daily activity plotted for a single member:

![activity](/docs/Anthony_daily_post_distribution.png)

### Logs

Logs from each script execution will be saved to the folder [/groupme_wrapped/logs/\<date\>.log](./logs/) and printed to the terminal. The log level can be set to:

* DEBUG
* INFO
* WARNING
* ERROR

Only log messages at the set log level in the [input argument](#execution), and higher level messages, will be displayed. For example, if the log level is set to `DEBUG`, log messages of levels `DEBUG`, `INFO`, `WARNING`, and `ERROR` will be printed to the terminal and saved to the log file. If the log lelevl is set to `WARNING`, only messages of level `WARNING` and `ERROR` will be logged. 
