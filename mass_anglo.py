import discord
from discord.ext import commands
import asyncio
import json
import os

# Intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

DM_DELAY = 2         # Delay per user
BATCH_SIZE = 20      # Number of users per batch
BATCH_DELAY = 3      # Delay between batches
CONFIG_FILE = "sent_users.json"

# Load previously messaged users
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
    """Send a mass DM to all server members in batches."""
    sent_count = 0
    failed_count = 0
    await ctx.send("Starting mass DM process...")

    members_to_message = [m for m in ctx.guild.members if not m.bot and str(m.id) not in sent_users]

    for i in range(0, len(members_to_message), BATCH_SIZE):
        batch = members_to_message[i:i+BATCH_SIZE]

        for member in batch:
            try:
                await member.send(message)
                sent_users[str(member.id)] = True
                sent_count += 1
                await asyncio.sleep(DM_DELAY)
            except discord.errors.HTTPException as e:
                if e.status == 429:
                    print(f"Rate limited while DMing {member}. Waiting 10 seconds...")
                    await asyncio.sleep(10)
                    try:
                        await member.send(message)
                        sent_users[str(member.id)] = True
                        sent_count += 1
                        await asyncio.sleep(DM_DELAY)
                    except:
                        failed_count += 1
                        print(f"Failed again to DM: {member}")
                else:
                    failed_count += 1
                    print(f"Failed to DM {member}: {e}")

        # Wait between batches
        await asyncio.sleep(BATCH_DELAY)

    # Save users who received the message
    with open(CONFIG_FILE, "w") as f:
        json.dump(sent_users, f)

    await ctx.send(f"Mass DM completed! Sent: {sent_count}, Failed: {failed_count}")

bot.run(os.getenv("DISCORD_TOKEN"))
