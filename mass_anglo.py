import discord
from discord.ext import commands
import asyncio
import json
import os
from flask import Flask  # Render port binding hack için

# ------------------ Discord Bot Ayarları ------------------

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

DM_DELAY = 2         # Delay per user in seconds
BATCH_SIZE = 20      # Number of users per batch
BATCH_DELAY = 3      # Delay between batches
CONFIG_FILE = "sent_users.json"

# Daha önce DM almış kullanıcıları yükle
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

# ------------------ Render Port Binding Hack ------------------

# Free Web Service için port binding
port = int(os.environ.get("PORT", 5000))
flask_app = Flask("bot")
@flask_app.route("/")
def home():
    return "Bot is running!"

# ------------------ Start Bot + Flask ------------------

if __name__ == "__main__":
    # Run Flask server in a separate thread so Discord bot da çalışır
    import threading
    threading.Thread(target=lambda: flask_app.run(host="0.0.0.0", port=port)).start()
    
    # Run Discord bot
    bot.run(os.getenv("DISCORD_TOKEN"))
