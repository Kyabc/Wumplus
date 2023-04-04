from __future__ import annotations

from typing import TYPE_CHECKING, Union

import discord
import openai
from discord import Interaction, app_commands
from discord.ext import commands

from app.config import settings

if TYPE_CHECKING:
    from bot import Wumpus

MESSAGES_LIMIT = 100

openai.api_key = settings.OPENAI_API_KEY


class ChatBot(commands.Cog):
    def __init__(self, bot: Wumpus) -> None:
        self.bot: Wumpus = bot
        self.channels: dict[int, dict[str, Union[str, bool]]] = dict()

    async def load_all_channel_messages(self, channel: discord.abc.GuildChannel) -> list[dict[str, str]]:
        messages = []
        async for message in channel.history(limit=MESSAGES_LIMIT):
            content = {
                "content": message.content,
                "role": "assistant" if message.author.id == self.bot.user.id else "user",
            }
            messages.append(content)
        return messages

    async def get_assistant_response(self, messages: list[dict[str, str]]) -> str:
        response = openai.ChatCompletion.create(model=settings.OPENAI_MODEL, messages=messages)
        assistant_response = response.choices[0].message.content
        return assistant_response

    @app_commands.command(name="create-channel", description="Create new channel under the same category")
    @app_commands.describe(name="new channel name")
    async def create_channel(self, interaction: Interaction, name: str) -> None:
        category = interaction.channel.category
        new_channel = await interaction.guild.create_text_channel(name=name, category=category)
        self.channels[new_channel.id] = {"type": "create", "participating": True, "webhook": interaction.followup}

    @app_commands.command(name="invite", description="Invite Wumpulus to this channel")
    async def invite(self, interaction: Interaction) -> None:
        channel_id = interaction.channel.id
        if channel_id in self.channels:
            # TODO: send embed msg ("Wumplus is already on this channel")
            pass
        else:
            self.channels[channel_id] = {"type": "invite", "participating": True, "webhook": interaction.followup}
            # TODO: send embed msg ("Wumplus joined this channel")

    @app_commands.command(name="delete-channel", description="Delete channel")
    async def delete_channel(self, interaction: Interaction) -> None:
        channel_id = interaction.channel.id
        if channel_id not in self.channels or self.channels[channel_id]["type"] != "create":
            # send embed msg ("this channel cannot be deleted")
            pass
        else:
            webhook = self.channels[channel_id]["webhook"]
            await interaction.channel.delete()
            # TODO: self embed msg ("this channel has been permanently deleted")
            self.channels.pop(channel_id)

    @app_commands.command(name="kick-Wumplus", description="Kick Wumplus from this channel")
    async def kick_wumplus(self, interaction: Interaction) -> None:
        channel = interaction.channel
        if channel.id not in self.channels:
            # send embed msg ("Wumplus is not on this channel")
            pass
        else:
            self.channels.pop(channel.id)
            # send embed msg ("Wumplus has left this channel")

    @app_commands.command(name="send", description="Send Message")
    @app_commands.describe(message="message")
    async def send_message(self, interaction: Interaction, message: str) -> None:
        all_messages = await self.load_all_channel_messages(interaction.channel)
        print("All message:", all_messages)
        all_messages.append({"content": message, "role": "user"})
        assistant_response = self.get_assistant_response(all_messages)
        await interaction.chennel.send(content=assistant_response)


async def setup(bot: Wumpus) -> None:
    await bot.add_cog(ChatBot(bot))
