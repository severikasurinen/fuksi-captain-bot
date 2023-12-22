# fuksi-captain-bot
Telegram bot to replace Captains' Hotline channel.

## Installation
Running the bot requires `python3` and `virtualenv` package. You can install `virtualenv` with
```console
python3 -m pip install --user virtualenv
```
or you can install it globally without `--user` flag or you can install it with you disributions package manager. Create virtual environment for bot with
```console
python3 -m venv env
```
and activate environment and install dependencies with
```console
source env/bin/activate
pip install -r requirements.txt
```
To start bot
```console
python3 bot.py
```

## Configuration
The bot is configured by modifying the `config.py` file.