from typing import Optional
import discord
from discord import app_commands
from lol_api_wrapper import LolApiWrapper
from dotenv import load_dotenv
import os
import json


MY_GUILD = discord.Object(id=1133835204671324371)  # replace with your guild id
DATA_PATH = "players.json"

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        # A CommandTree is a special type that holds all the application command
        # state required to make it work. This is a separate class because it
        # allows all the extra state to be opt-in.
        # Whenever you want to work with application commands, your tree is used
        # to store and work with them.
        # Note: When using commands.Bot instead of discord.Client, the bot will
        # maintain its own tree instead.
        load_dotenv(dotenv_path="config")
        self.tree = app_commands.CommandTree(self)
        self.lolapi = LolApiWrapper(os.getenv("LOL_API_TOKEN"), "europe")
        self.leaderboard = {}
        with open(DATA_PATH, 'r') as file:
            self.leaderboard = json.load(file)

    # In this basic example, we just synchronize the app commands to one guild.
    # Instead of specifying a guild to every command, we copy over our global commands instead.
    # By doing so, we don't have to wait up to an hour until they are shown to the end-user.
    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.default()
client = MyClient(intents=intents)


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')


@client.tree.command()
async def monkeyboard(interaction: discord.Interaction):
    """List the monkeys"""

    if not client.leaderboard:
        await interaction.response.send_message("No monkeys registered in the leaderboard yet!")
    else:
        embed = discord.Embed(title='Monkeyboard')
        leaderboard_message = "\n".join([f"{key}" for key, _ in client.leaderboard.items()])
        embed.description = leaderboard_message
        await interaction.response.send_message(embed=embed)


@client.tree.command()
@app_commands.describe(
    gamename='The player name',
    tagline='The player tagLine'
)
async def addmonkey(interaction: discord.Interaction, gamename: str, tagline: str):
    """Add a monkey to the leaderboard"""
    if client.leaderboard.get(f"{gamename}#{tagline}"):
        await interaction.response.send_message(f"The monkey is already registered")
        return

    msg = ""
    try:
        account = client.lolapi.get_account_by_id(gamename, tagline)
        client.leaderboard[f"{gamename}#{tagline}"] = account["puuid"]
        msg = f"{gamename}#{tagline} has been successfully added to the monkey list.\n"
        with open(DATA_PATH, 'w') as file:
            json.dump(client.leaderboard, file)

    except Exception as e:
        msg = f"{e}"
    finally:
        await interaction.response.send_message(msg)

client.run(os.getenv("DISCORD_TOKEN"))