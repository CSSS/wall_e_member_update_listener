import logging
import os

import django
from django.core.wsgi import get_wsgi_application


from setup_logger import Loggers

log_info = Loggers.get_logger(logger_name="member_update_listener")
member_update_listener_log = log_info[0]


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_settings")
django.setup()

application = get_wsgi_application()

import discord
from discord import Intents
from discord.ext import commands

from wall_e_models.models import UpdatedUser


bot = commands.Bot(command_prefix='.', intents=Intents.all())


@bot.listen(name="on_ready")
async def ready():
    member_update_listener_log.info("member update listener is now up")


@bot.listen(name="on_command_error")
async def func(ctx, error):
    if type(error) != commands.CommandNotFound:
        member_update_listener_log.error(error)


@bot.listen(name="on_member_update")
async def on_member_update(member_before_update, member_after_update):
    await mark_user_as_updated(member_after_update)


@bot.listen(name="on_message")
async def on_message(message):
    await mark_user_as_updated(message.author)


@bot.listen(name="on_member_join")
async def new_member(member: discord.Member):
    await mark_user_as_updated(member)


async def mark_user_as_updated(member: discord.Member):
    user_to_update = await UpdatedUser.user_update_is_unique(member)
    if user_to_update is not None:
        member_update_listener_log.info(f"marking user {member} as needing an update")
        await UpdatedUser(user_point=user_to_update).async_save()


discordpy_logger_name = "discord.py"


class DiscordPyDebugStreamHandler(logging.StreamHandler):
    def __init__(self):
        super(DiscordPyDebugStreamHandler, self).__init__()

    def emit(self, record):
        if record.name != discordpy_logger_name:
            for handler in discordpy_logger.handlers:
                if record.levelno >= handler.level:
                    handler.emit(record)


discordpy_log_info = Loggers.get_logger(logger_name=discordpy_logger_name)
discordpy_logger = discordpy_log_info[0]

bot.run(token=os.environ["basic_config__TOKEN"], log_handler=DiscordPyDebugStreamHandler())
