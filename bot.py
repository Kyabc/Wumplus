from __future__ import annotations

import asyncio
import sys
import traceback

import aiohttp
import discord
from discord.ext import commands
from discord.ext.commands import ExtensionFailed, ExtensionNotFound, NoEntryPointError

from app.config import settings

initial_extensions = ["app.cogs.chatbot"]

intents = discord.Intents.default()
intents.message_content = True

BOT_PREFIX = "-"


class Wumpus(commands.Bot):
    debug: bool
    bot_app_info: discord.AppInfo

    def __init__(self) -> None:
        super().__init__(command_prefix=BOT_PREFIX, case_insensitive=True, intents=intents)
        self.session: aiohttp.ClientSession = None
        self.bot_version = "0.1.0"

    async def on_ready(self) -> None:
        await self.tree.sync()
        print(f"Logged in as: {self.user} (Bot Version: {self.bot_version})\n")
        

    async def setup_hook(self) -> None:
        if self.session is None:
            self.session = aiohttp.ClientSession()
        await self.load_cogs()

    async def load_cogs(self) -> None:
        for ext in initial_extensions:
            try:
                await self.load_extension(ext)
                print(f"Success to load extension {ext}")
            except (
                ExtensionNotFound,
                NoEntryPointError,
                ExtensionFailed,
            ):
                print(f"Failed to load extension {ext}.", file=sys.stderr)
                traceback.print_exc()

    async def close(self) -> None:
        await self.session.close()
        await super().close()

    async def start(self, debug: bool = False) -> None:
        self.debug = debug
        return await super().start(settings.DISCORD_TOKEN, reconnect=True)


def run_bot() -> None:
    bot = Wumpus()
    asyncio.run(bot.start())


if __name__ == "__main__":
    run_bot()
