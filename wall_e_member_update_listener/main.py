import os

import django
from django.core.wsgi import get_wsgi_application

from discordpy_stream_handler import DiscordPyDebugStreamHandler
from loggers import member_update_listener_log

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_settings")
django.setup()

application = get_wsgi_application()

import discord
from discord import Intents
from discord.ext import commands

from wall_e_models.models import UpdatedUser


bot = commands.Bot(command_prefix='.', intents=Intents.all())


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
        member_update_listener_log.info(f"marking user {member} as needed an update")
        await UpdatedUser(user_point=user_to_update).async_save()


bot.run(token=os.environ["basic_config__TOKEN"], log_handler=DiscordPyDebugStreamHandler())
