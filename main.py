import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

# Load .env if running locally (ignored on Render)
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True  # Required for message content access
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

RULE_CHANNEL_NAME = "rules"
rules = []

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await tree.sync()
        print(f"🔁 Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

# Slash command to add a rule
@tree.command(name="addrule", description="Add a new rule to the rule list.")
@app_commands.describe(rule_text="The rule you want to add.")
async def addrule(interaction: discord.Interaction, rule_text: str):
    global rules
    rule_number = len(rules) + 1
    rule_message = f"Rule {rule_number}. {rule_text}"
    rules.append(rule_message)

    # Find the rules channel
    channel = discord.utils.get(interaction.guild.text_channels, name=RULE_CHANNEL_NAME)
    if not channel:
        await interaction.response.send_message("❌ 'rules' channel not found.", ephemeral=True)
        return

    try:
        await channel.send(rule_message)
        await interaction.response.send_message(f"✅ Rule added: {rule_message}", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("❌ Missing permissions to post in the rules channel.", ephemeral=True)

# Optional: Allow !NewRule as well (legacy message command)
@bot.command(name="NewRule")
async def new_rule_legacy(ctx, *, rule_text: str):
    rule_number = len(rules) + 1
    rule_message = f"Rule {rule_number}. {rule_text}"
    rules.append(rule_message)

    channel = discord.utils.get(ctx.guild.text_channels, name=RULE_CHANNEL_NAME)
    if not channel:
        await ctx.send("❌ 'rules' channel not found.")
        return

    try:
        await channel.send(rule_message)
        await ctx.send(f"✅ Rule added: {rule_message}")
    except discord.Forbidden:
        await ctx.send("❌ Missing permissions to post in the rules channel.")

token = os.getenv("TOKEN")
if not token:
    print("❌ ERROR: TOKEN environment variable not set. Please set it in your .env or on Render.")
else:
    print("✅ TOKEN loaded successfully, starting bot...")
    bot.run(token)
