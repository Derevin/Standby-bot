import os
import pytz
import nextcord

NO_SSL = os.getenv("NO_SSL", False)
NODB = os.getenv("NODB", False)
BOT_TOKEN = str(os.getenv("BOT_TOKEN", False))
BOT_ID = int(os.getenv("BOT_ID", False))
DATABASE_URL = str(os.getenv("DATABASE_URL", False))
GUILD_ID = int(os.getenv("GUILD_ID", False))
STARBOARD_ID = int(os.getenv("STARBOARD_ID", False))
GINNY_TRANSPARENT_URL = str(os.getenv("GINNY_TRANSPARENT_URL", False))
GINNY_WHITE_URL = str(os.getenv("GINNY_WHITE_URL", False))
BOT_TZ = pytz.timezone(os.getenv("TZ", "UTC"))

DB_TMER_REMINDER = 1
DB_TMER_GIVEAWAY = 2
DB_TMER_REPOST = 3
DB_TMER_ROULETTE = 4

ERROR_CHANNEL_NAME = "maintenance-channel"
ERROR_CHANNEL_ID = 376031149371162635
NO_RESPONSE_CHANNELS = [
    "mod-chat",
    "rules",
    "giveaways",
    "alliance-mod-chat",
    "starboard",
    "events",
    "event-submission",
]
GIVEAWAY_CHANNEL_NAME = "giveaways"
LOGS_CHANNEL_NAME = "mod-log"
INVITE_LINK = "https://discord.gg/x7nsqEj"
MOD_ROLES = ["Moderator", "Guides of the Void"]
MODS_AND_GUIDES = nextcord.Permissions(manage_messages=True)
MODS_ONLY = nextcord.Permissions(ban_members=True)
REEPOSTER_NAME = "REE-poster"
REEPOSTER_EMOJI = "FEELSREEE"
BIRTHDAY_NAME = "Birthday Haver"
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
EMPTY = "\u200b"
EMPTY2 = "᲼"
TADA = "🎉"
FEL_ID = 235055132843180032
DER_ID = 295553857054834690
JORM_ID = 168350377824092160
BOT_SPAM_ID = 748506600880210452
GENERAL_ID = 315247766739615745
GIT_STATIC_URL = "https://raw.githubusercontent.com/Derevin/Standby-bot/main/static/"
DARKNESS_ID = 238021076406370304
AIRU_ID = 378272190782504960
MAX_MENU_SIZE = 25
