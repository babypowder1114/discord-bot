import discord
import gspread
import os
import json
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds_json = json.loads(os.environ["GOOGLE_CREDS"])
creds = Credentials.from_service_account_info(creds_json, scopes=SCOPES)

gc = gspread.authorize(creds)
sheet = gc.open("イカ出欠確認").worksheet("出欠反映")
db_sheet = gc.open("イカ出欠確認").worksheet("メンバーDB")

intents = discord.Intents.default()
intents.reactions = True
intents.members = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print("起動成功")

@client.event
async def on_raw_reaction_add(payload):

    guild = client.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id) or await guild.fetch_member(payload.user_id)

    discord_id = str(member.id)

    db_values = db_sheet.get_all_values()

    nickname = None
    for row in db_values[1:]:
        if row and row[0] == discord_id:
            nickname = row[2]
            break

    if nickname is None:
        nickname = member.name

    values = sheet.get_all_values()

    row_index = None
    for i, row in enumerate(values[1:], start=2):
        if row and row[0] == nickname:
            row_index = i
            break

    if row_index is None:
        sheet.append_row([nickname, "", "", "", ""])
        values = sheet.get_all_values()
        row_index = len(values)

    emoji = str(payload.emoji)

    if "🔴" in emoji:
        sheet.update_cell(row_index, 2, "○")
    elif "🔵" in emoji:
        sheet.update_cell(row_index, 3, "○")
    elif "🟡" in emoji:
        sheet.update_cell(row_index, 4, "○")

@client.event
async def on_raw_reaction_remove(payload):

    guild = client.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id) or await guild.fetch_member(payload.user_id)

    discord_id = str(member.id)

    db_values = db_sheet.get_all_values()

    nickname = None
    for row in db_values[1:]:
        if row and row[0] == discord_id:
            nickname = row[2]
            break

    if nickname is None:
        nickname = member.name

    values = sheet.get_all_values()

    row_index = None
    for i, row in enumerate(values[1:], start=2):
        if row and row[0] == nickname:
            row_index = i
            break

    if row_index is None:
        return

    emoji = str(payload.emoji)

    if "🔴" in emoji:
        sheet.update_cell(row_index, 2, "")
    elif "🔵" in emoji:
        sheet.update_cell(row_index, 3, "")
    elif "🟡" in emoji:
        sheet.update_cell(row_index, 4, "")

TOKEN = os.environ["TOKEN"]
client.run(TOKEN)