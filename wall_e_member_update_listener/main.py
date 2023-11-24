import asyncio
import logging
import os

import aiohttp
import django
from discord.app_commands import CommandNotFound
from django.core.wsgi import get_wsgi_application


from setup_logger import Loggers

log_info = Loggers.get_logger(logger_name="member_update_listener")
member_update_listener_log = log_info[0]
member_update_listener_debug_log_file_absolute_path = log_info[1]
member_update_listener_warn_log_file_absolute_path = log_info[2]
member_update_listener_error_log_file_absolute_path = log_info[3]

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_settings")
django.setup()

application = get_wsgi_application()

import discord
from discord import Intents
from discord.ext import commands

from wall_e_models.models import UpdatedUser


bot = commands.Bot(command_prefix='.', intents=Intents.all(), help_command=None)


@bot.listen(name="on_ready")
async def ready():
    bot.loop.create_task(
        write_to_bot_log_channel(
            member_update_listener_log, member_update_listener_debug_log_file_absolute_path,
            1174032003109240902
        )
    )
    bot.loop.create_task(
        write_to_bot_log_channel(
            member_update_listener_log, member_update_listener_warn_log_file_absolute_path,
            1174032047552086107
        )
    )
    bot.loop.create_task(
        write_to_bot_log_channel(
            member_update_listener_log, member_update_listener_error_log_file_absolute_path,
            1174032090069737493
        )
    )

    bot.loop.create_task(
        write_to_bot_log_channel(
            member_update_listener_log, discordpy_debug_log_file_absolute_path,
            1174032132851634177
        )
    )
    bot.loop.create_task(
        write_to_bot_log_channel(
            member_update_listener_log, discordpy_warn_log_file_absolute_path,
            1174032176065560777
        )
    )
    bot.loop.create_task(
        write_to_bot_log_channel(
            member_update_listener_log, discordpy_error_log_file_absolute_path,
            1174032220227375235
        )
    )
    member_update_listener_log.info("member update listener is now up")


@bot.listen(name="on_command_error")
async def func(ctx, error):
    if type(error) != commands.CommandNotFound:
        member_update_listener_log.error(error)

async def slash_func(interaction, error):
    if type(error) != CommandNotFound:
        member_update_listener_log.error(error)

bot.tree.on_error = slash_func

@bot.listen(name="on_member_update")
async def on_member_update(member_before_update, member_after_update):
    await mark_user_as_updated(member_after_update)


@bot.listen(name="on_message")
async def on_message(message):
    await mark_user_as_updated(message.author)


@bot.listen(name="on_member_join")
async def new_member(member: discord.Member):
    await mark_user_as_updated(member)


async def mark_user_as_updated(member):
    user_to_update = await UpdatedUser.outdated_user_profile(member)
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
discordpy_debug_log_file_absolute_path = discordpy_log_info[1]
discordpy_warn_log_file_absolute_path = discordpy_log_info[2]
discordpy_error_log_file_absolute_path = discordpy_log_info[3]


async def write_to_bot_log_channel(logger, file_path, chan_id):
    """
    Takes care of opening a file and keeping it opening while reading from it and uploading it's contents
     to the specified channel
    :param logger: the service's logger instance
    :param config: used to determine the gmail credentials
    :param bot: needed to get the channel ID for the channel that the logs will be sent to and ensure the
     while loop only runs while bot.is_closed() is False
    :param file_path: the path of the log file to upload to the text channel
    :param chan_id: the ID of the channel that the log file lines will be uploaded to
    :param error_channel: indicator of whether chan_id is for an error channel and therefore error emails
     may need to be sent
    :return:
    """
    channel = discord.utils.get(
        bot.guilds[0].channels, id=chan_id
    )
    logger.debug(
        f"[log_channel.py write_to_bot_log_channel()] {channel} channel "
        f"with id {chan_id} successfully retrieved."
    )
    f = open(file_path, 'r')
    f.seek(0)
    while not bot.is_closed():
        f.flush()
        line = f.readline()
        while line:
            if line.strip() != "":
                # this was done so that no one gets accidentally pinged from the bot log channel
                line = line.replace("@", "[at]")
                output = line
                # done because discord has a character limit of 2000 for each message
                # so what basically happens is it first tries to send the full message, then if it cant, it
                # breaks it down into 2000 sizes messages and send them individually
                try:
                    await channel.send(output)
                except (aiohttp.ClientError, discord.errors.HTTPException):
                    finished = False
                    first_index, last_index = 0, 2000
                    while not finished:
                        await channel.send(output[first_index:last_index])
                        first_index = last_index
                        last_index += 2000
                        if len(output[first_index:last_index]) == 0:
                            finished = True
                except RuntimeError:
                    logger.debug(
                        "[log_channel.py write_to_bot_log_channel()] encountered RuntimeError, "
                        " will assume that the user is attempting to exit"
                    )
                    break
                except Exception as exc:
                    exc_str = f'{type(exc).__name__}: {exc}'
                    raise Exception(
                        f'[log_channel.py write_to_bot_log_channel()] write to channel failed\n{exc_str}'
                    )
            line = f.readline()
        await asyncio.sleep(1)


bot.run(token=os.environ["basic_config__TOKEN"], log_handler=DiscordPyDebugStreamHandler())
