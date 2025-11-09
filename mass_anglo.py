import discord
from discord.ext import commands
import asyncio
import json
import os

# Intents (required for accessing members and command messages)
intents = discord.Intents.default()
intents.members = True
intents.message_content = True  # Needed to read command messages

bot = commands.Bot(command_prefix="!", intents=intents)

DM_DELAY = 1  # Delay per user to avoid hitting rate limits
CONFIG_FILE = "sent_users.json"

# Load users who already received the DM
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f:
        sent_users = json.load(f)
else:
    sent_users = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")

@bot.command()
async def mass_dm(ctx, *, message):
    """Send a mass DM to all server members (excluding bots and already messaged users)."""
    sent_count = 0
    failed_count = 0
    
    await ctx.send("Starting to send messages...")

    for member in ctx.guild.members:
        if not member.bot:
            if str(member.id) in sent_users:
                continue  # Already sent a DM, skip
            try:
                # Send the DM
                await member.send(message)
                sent_users[str(member.id)] = True
                sent_count += 1
                await asyncio.sleep(DM_DELAY)
            except:
                failed_count += 1
                print(f"Could not DM: {member}")

    # Save users who received the message
    with open(CONFIG_FILE, "w") as f:
        json.dump(sent_users, f)
    
    await ctx.send(f"Mass DM completed! Sent: {sent_count}, Failed: {failed_count}")

# Run the bot using environment variable for token (Render-safe)
bot.run(os.getenv("DISCORD_TOKEN"))
