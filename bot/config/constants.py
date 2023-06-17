from datetime import timedelta as _timedelta
from os import getenv
from pathlib import Path

from nextcord import Permissions, TextChannel, Thread, VoiceChannel
from pytz import timezone

# Environment variables
NO_SSL = getenv("NO_SSL", False)
NODB = getenv("NODB", False)
BOT_TOKEN = str(getenv("BOT_TOKEN", False))
BOT_ID = int(getenv("BOT_ID", False))
DATABASE_URL = str(getenv("DATABASE_URL", False))
GUILD_ID = int(getenv("GUILD_ID", False))
STARBOARD_ID = int(getenv("STARBOARD_ID", False))
ERROR_CHANNEL_ID = int(getenv("ERROR_CHANNEL_ID", False))
GINNY_TRANSPARENT_URL = str(getenv("GINNY_TRANSPARENT_URL", False))
GINNY_WHITE_URL = str(getenv("GINNY_WHITE_URL", False))
BOT_TZ = timezone(getenv("TZ", "UTC"))
OPENAI_API_KEY = getenv("OPENAI_API_KEY", False)

# Channels
OFFERS_CHANNEL_NAME = "offers"
GIVEAWAY_CHANNEL_NAME = "giveaways"
LOGS_CHANNEL_NAME = "mod-log"
RULES_CHANNEL_NAME = "getting-started"
ERROR_CHANNEL_NAME = "maintenance-channel"
NO_RESPONSE_CHANNELS = ["mod-chat", RULES_CHANNEL_NAME, GIVEAWAY_CHANNEL_NAME, "alliance-mod-chat", "starboard",
                        "events", "event-submissions"]
GENERAL_ID = 315247766739615745
GIVEAWAYS_ID = 366906148500275200
TICKET_CHANNEL_ID = 994974670275223673
RULES_MESSAGE_ID = 754461970488492032
BOT_SPAM_ID = 343465942199828481

# Roles and permissions
MOD_ROLE_NAMES = ["Moderator", "Guides of the Void"]
REEPOSTER_NAME = "REE-poster"
REEPOSTER_EMOJI = "FEELSREEE"
BIRTHDAY_NAME = "Birthday Haver"
MODS_AND_GUIDES = Permissions(kick_members=True)
MODS_ONLY = Permissions(ban_members=True)
MANAGE_EMOJIS = Permissions(manage_emojis=True)

# Users
FEL_ID = 235055132843180032
DER_ID = 295553857054834690
JORM_ID = 168350377824092160
DARKNESS_ID = 238021076406370304
AIRU_ID = 378272190782504960
ANA_ID = 421039678481891348
KROSS_ID = 255653858095661057

# Timer enums
DB_TMER_REMINDER = 1
DB_TMER_GIVEAWAY = 2
DB_TMER_REPOST = 3
DB_TMER_ROULETTE = 4
DB_TMER_BURGER = 5

# Color hexcodes
SOFT_RED = 0xCD6D6D
STARBOARD_COLOUR = 0xFFAC33
DARK_BLUE = 0x00008B
DARK_ORANGE = 0xFF5E13
PALE_GREEN = 0xBCF5BC
PALE_YELLOW = 0xFDFF96
GREY = 0x6A6866
PALE_BLUE = 0xADD8E6
LIGHT_BLUE = 0x1F75FE
VIE_PURPLE = 0xA569BD

# Special strings
EMPTY = "\u200b"
EMPTY2 = "᲼"
TADA = "🎉"

# Starboard
STAR_THRESHOLD = 4

# Links
INVITE_LINK = "https://discord.gg/x7nsqEj"
GIT_STATIC_URL = "https://raw.githubusercontent.com/Derevin/Standby-bot/main/static/"
LOCAL_STATIC_PATH = Path(__file__).parent.parent.parent / "static"
DISCORD_MESSAGE_LINK_PATTERN = r"https:\/\/(\w+\.)?discord(app)?\.com\/channels\/\d+\/\d+\/\d+"

# Rules channel content
MAX_MENU_SIZE = 24
RULES_LIST = ["1. Respect all other members.", "2. Keep conversations friendly and calm.",
              "3. No impersonating a moderator, or any others.", "4. No inappropriate names or avatars.",
              "5. No hate speech or slurs of any kind.", "6. No advertising or spam.",
              "7. No links to or posting NSFW content, including pornography, gore and sexualised lolis.",
              "8. Listen to moderators.",
              f"9. Do not appeal mod decisions in public channels - open a ticket in <#{TICKET_CHANNEL_ID}>.",
              "10. No attacking race, religion, sexual orientation, gender identity or "
              "nationality.", f"11. Keep bot commands in <#{BOT_SPAM_ID}> unless it's relevant to the "
                              "current conversation.", "12. Don't ping clan roles, @here or @everyone"]

GENERAL_INFO = (
    f"Talking in the server awards XP - you need Level 3 to access <#{GIVEAWAYS_ID}>. Enforcement of the rules is "
    "always at the moderators' discretion. Repeated infractions within a 30 day period lead to automatic action:\n"
    "2 Warns = Muted for a day\n"
    "3 Warns = Muted for 3 days\n"
    "4 Warns = Banned for 7 days\n"
    "5 Warns = Permanent ban")

DELIMITERS = {"clan": "Clans", "opt-in": "Opt-in", "color": "Colors"}

PRIO_ROLES = ["UpdateSquad", "Vie for the Void"]

ROLE_DESCRIPTIONS = {"Offers": f"News about free or discounted games in #{OFFERS_CHANNEL_NAME}",
                     "UpdateSquad": "Get notified about server changes, giveaways, events, polls etc"}

# Tickets
CLAIMABLE_TICKETS_CAT_NAME = "Talk to mods"
CLAIMABLE_CHANNEL_NAME = "ticket-channel"
ACTIVE_TICKETS_CAT_NAME = "Active tickets"
RESOLVED_TICKETS_CAT_NAME = "Resolved tickets"
TICKETS_LOG_CHANNEL_NAME = "tickets-log"
CLAIMABLE_CHANNEL_MESSAGE = ("If you have an issue and want to talk to the mod team, this is the place.\nPress "
                             "the button to open a ticket in a private channel visible only to you and the mod team.")
CLAIMED_MESSAGE = ("You have successfully opened a ticket - please let us know what you want to discuss.\n"
                   "You can make sure you're talking only to the mod team by looking "
                   "at the channel's current member list (right side of discord).\n"
                   "Once this issue has been resolved, use the `/resolve` command.")
RESOLVED_MESSAGE = ("This ticket has been marked as resolved. If this was a mistake or you have additional questions, "
                    "use the button below to reopen the ticket.\nFor other issues, please create a new ticket in XXX.\n"
                    "Moderators can use the Scrap button to scrap this ticket. (Scrapping takes a while to complete)")
REOPENED_MESSAGE = "This ticket has been reopened. Once it is resolved, use the `/resolve` command again."

# Roulette
ROULETTE_TIMEOUT = _timedelta(minutes=30)

# Reputation
THANK_TYPE = "Void"

# Burger
BURGER_TIMEOUT = _timedelta(weeks=1)
BURGER_QUESTIONS = [
    dict(question="How much does the average American ambulance trip cost?", correct=["$1200"], wrong=["$200", "$800"]),
    dict(question="How many Americans think the sun revolves around the earth?", correct=["1 in 4"],
         wrong=["1 in 2", "1 in 3", "1 in 5"]),
    dict(question="How many avocados do Americans eat a year combined?", correct=["4.2 bn"], wrong=["2 bn", "6.5 bn"]),
    dict(question="How many Americans get injuries related to a TV falling every year?", correct=["11 800"],
         wrong=["5 200", "13 900"])]

# Reposts
REPOSTER_DURATION = _timedelta(days=1)
REE_THRESHOLD = 4

# Warframe
WARFRAME_MODS_URL = "https://raw.githubusercontent.com/WFCD/warframe-items/master/data/json/Mods.json"

# Misc
VALID_TEXT_CHANNEL = TextChannel | VoiceChannel | Thread
