import asyncio
import os
import requests
import discord
import logging
from datetime import datetime
from flask import Flask
from threading import Thread
import time
import urllib.request

# ------------------ READ TOKENS FROM ENVIRONMENT ------------------
DISCORD_TOKEN = "8761714864:AAH3ZuTJYCMoFRmFtNHePzTO8rNwckYnVXw"
TELEGRAM_BOT_TOKEN = "8134660761"
TELEGRAM_CHAT_ID = "MTQxOTA2NDAwMjI4MDk1MTg0OA.GxLBFf.HgG5TXsmpbo3F-YXsCvi8oadJEEUGeOMf88izM"

# Check if tokens are present
if not DISCORD_TOKEN:
    raise Exception("❌ DISCORD_TOKEN environment variable not set.")
if not TELEGRAM_BOT_TOKEN:
    raise Exception("❌ TELEGRAM_TOKEN environment variable not set.")
if not TELEGRAM_CHAT_ID:
    raise Exception("❌ CHAT_ID environment variable not set.")

# ------------------ SERVERS TO MONITOR ------------------
SERVERS = {
    "1196857788220067943": "Variational",
    "667044843901681675": "Optimism",
    "1364669301751283793": "Solflare",
    "925207817923743794": "SOL Decoder",
    "402910780124561410": "Compound",
    "978714252934258779": "Zcash",
    "1240797310196125857": "Lombard",
    "1255553987206447194": "OP_NET",
    "1296015181985349715": "STBL",
    "1381686363233194004": "Bullpen",
    "710897173927297116": "Polymarket",
    "1024239646357594122": "THENA",
    "1230430080514396161": "Yei Finance",
    "1209575590362095676": "Avalon Labs",
    "943473409541685319": "Camelot DEX",
    "1139242134495559801": "SPARK DotFi",
    "551050633898360852": "Fluid",
    "841556000632078378": "Bullet",
    "491256308461207573": "Algorand",
    "1329085279411245088": "Falcon Finance",
    "895116209958297631": "LoopScale",
    "793925570739044362": "Goldfinch",
    "885256081289379850": "Ledger OP3N",
    "1385014051272265868": "Shelby",
    "1219739501673451551": "MegaETH",
    "1443079201996410987": "Alien",
    "334085157441110017": "Horizen",
    "1165826384975908924": "Midnight Network",
    "473781666251538452": "Build on Circle",
    "933846070344167464": "Moonwell Fi",
    "839766295808311306": "Telcoin",
    "1270276651636232282": "Pharos",
}

IGNORE_SERVERS = {
    "703994580499955784",  # Double Counter
    "1067165013397213286", # Base
}

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
logging.getLogger('discord').setLevel(logging.ERROR)

def send_tg(text, parse_mode="Markdown"):
    try:
        requests.post(
            f"{TELEGRAM_API}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": text[:4096], "parse_mode": parse_mode},
            timeout=5
        )
    except Exception as e:
        print(f"Telegram error: {e}")

# ------------------ KEEP-ALIVE WEB SERVER ------------------
app = Flask(__name__)

@app.route('/')
def home():
    return "Discord self‑bot is running 24/7."

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web_server)
    t.daemon = True
    t.start()

def self_ping():
    host = os.environ.get("RENDER_EXTERNAL_URL")
    if not host:
        print("RENDER_EXTERNAL_URL not set; self‑ping disabled.")
        return
    url = f"{host}/"
    while True:
        try:
            urllib.request.urlopen(url, timeout=10)
            print(f"Self‑ping sent to {url}")
        except Exception as e:
            print(f"Self‑ping failed: {e}")
        time.sleep(120)

def start_self_ping():
    t = Thread(target=self_ping)
    t.daemon = True
    t.start()

# ------------------ DISCORD CLIENT ------------------
client = discord.Client()

@client.event
async def on_ready():
    msg = f"✅ Bot online as {client.user}\nMonitoring {len(SERVERS)} servers"
    send_tg(msg)
    print(msg)

@client.event
async def on_member_join(member):
    gid = str(member.guild.id)
    if gid in IGNORE_SERVERS or gid not in SERVERS:
        return
    name = SERVERS[gid]
    send_tg(f"🚀 **{name}**\n👤 {member.name} joined\n🆔 {member.id}\n👥 Total: {member.guild.member_count}")

@client.event
async def on_member_remove(member):
    gid = str(member.guild.id)
    if gid in IGNORE_SERVERS or gid not in SERVERS:
        return
    name = SERVERS[gid]
    send_tg(f"👋 **{name}**\n👤 {member.name} left\n🆔 {member.id}")

@client.event
async def on_message(message):
    if message.author.bot:
        return
    gid = str(message.guild.id)
    if gid in IGNORE_SERVERS or gid not in SERVERS:
        return
    name = SERVERS[gid]
    content = message.content[:200].replace('\n', ' ')
    send_tg(f"💬 **{name}** #{message.channel.name}\n👤 {message.author}\n📝 {content}")

@client.event
async def on_message_edit(before, after):
    if before.author.bot:
        return
    gid = str(before.guild.id)
    if gid in IGNORE_SERVERS or gid not in SERVERS:
        return
    name = SERVERS[gid]
    before_text = before.content[:100]
    after_text = after.content[:100]
    send_tg(f"✏️ **{name}** #{before.channel.name}\n👤 {before.author}\n📝 Before: {before_text}\n➡️ After: {after_text}")

@client.event
async def on_message_delete(message):
    if message.author.bot:
        return
    gid = str(message.guild.id)
    if gid in IGNORE_SERVERS or gid not in SERVERS:
        return
    name = SERVERS[gid]
    content = message.content[:200]
    send_tg(f"🗑️ **{name}** #{message.channel.name}\n👤 {message.author}\n❌ Deleted: {content}")

@client.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return
    gid = str(reaction.message.guild.id)
    if gid in IGNORE_SERVERS or gid not in SERVERS:
        return
    name = SERVERS[gid]
    send_tg(f"👍 **{name}**\n👤 {user} reacted {reaction.emoji} to {reaction.message.author}")

@client.event
async def on_voice_state_update(member, before, after):
    gid = str(member.guild.id)
    if gid in IGNORE_SERVERS or gid not in SERVERS:
        return
    name = SERVERS[gid]
    if before.channel is None and after.channel is not None:
        send_tg(f"🎤 **{name}**\n👤 {member} joined voice: {after.channel.name}")
    elif before.channel is not None and after.channel is None:
        send_tg(f"🔇 **{name}**\n👤 {member} left voice: {before.channel.name}")
    elif before.channel != after.channel:
        send_tg(f"🔄 **{name}**\n👤 {member} moved from {before.channel.name} to {after.channel.name}")

@client.event
async def on_presence_update(before, after):
    if after.bot:
        return
    gid = str(after.guild.id)
    if gid in IGNORE_SERVERS or gid not in SERVERS:
        return
    name = SERVERS[gid]
    if before.status != after.status:
        send_tg(f"🟢 **{name}**\n👤 {after.name} status: {after.status}")

@client.event
async def on_guild_role_create(role):
    gid = str(role.guild.id)
    if gid in SERVERS:
        name = SERVERS[gid]
        send_tg(f"🏷️ **{name}**\nRole created: {role.name}")

@client.event
async def on_guild_role_delete(role):
    gid = str(role.guild.id)
    if gid in SERVERS:
        name = SERVERS[gid]
        send_tg(f"🗑️ **{name}**\nRole deleted: {role.name}")

@client.event
async def on_audit_log_entry_create(entry):
    gid = str(entry.guild.id)
    if gid in SERVERS:
        name = SERVERS[gid]
        action = str(entry.action)
        target = str(entry.target)
        user = entry.user
        send_tg(f"📜 **{name}**\n👮 {user} did {action} on {target}")

# ------------------ RUN ------------------
if __name__ == "__main__":
    keep_alive()
    start_self_ping()
    print("Starting full surveillance bot with keep‑alive...")
    try:
        # Use asyncio.run to avoid event loop issues
        asyncio.run(client.start(DISCORD_TOKEN))
    except discord.LoginFailure:
        print("❌ Invalid Discord token. Check DISCORD_TOKEN environment variable.")
        send_tg("❌ Bot failed: Invalid Discord token.")
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        send_tg(f"❌ Bot crashed: {str(e)[:200]}")
