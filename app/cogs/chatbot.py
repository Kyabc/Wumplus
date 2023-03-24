from __future__ import annotations

from typing import TYPE_CHECKING

import discord
import openai
from discord import Interaction, app_commands
from discord.ext import commands

from app.config import settings

if TYPE_CHECKING:
    from bot import Wumpus


openai.api_key = settings.OPENAI_API_KEY


class ChatBot(commands.Cog):
    def __init__(self, bot: Wumpus) -> None:
        self.bot: Wumpus = bot
        self.chatbot_channel_id: list[discord.TextChannel] = []

    async def load_all_channel_messages(self, channel: discord.abc.GuildChannel) -> list[dict[str, str]]:
        last_message_id = None
        messages = []
        while True:
            message_list = await channel.history(limit=1000, before=last_message_id)
            if message_list:
                for msg in message_list:
                    content = {
                        "content": msg.content,
                        "role": "assistant" if msg.author.id == self.bot.user.id else "user",
                    }
                    messages.append(content)
            else:
                break
            last_message_id = message_list[-1].id
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
        self.chatbot_channel_id.append(new_channel)

    # @app_commands.command(name="delete-channel", description="Delete channel")
    # async def delete_channel():
    #     TODO: Implement a command to delete channels created by this bot

    @app_commands.command(name="send", description="Send Message")
    @app_commands.describe(message="message")
    async def send_message(self, interaction: Interaction, message: str):
        all_messages = await self.load_all_channel_messages(interaction.channel)
        all_messages.append({"content": message, "role": "user"})
        assistant_response = self.get_assistant_response(all_messages)
        await interaction.chennel.send(content=assistant_response)


async def setup(bot: Wumpus) -> None:
    await bot.add_cog(ChatBot(bot))
