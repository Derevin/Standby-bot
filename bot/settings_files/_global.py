import os

NODB = os.getenv("NODB", False)
BOT_TOKEN = str(os.getenv("BOT_TOKEN", False))
BOT_ID = int(os.getenv("BOT_ID", False))
DATABASE_URL = str(os.getenv("DATABASE_URL", False))
GUILD_ID = int(os.getenv("GUILD_ID", False))
STARBOARD_ID = int(os.getenv("STARBOARD_ID", False))


ERROR_CHANNEL_NAME = "maintenance-channel"
MOD_ROLES_NAMES = ["Moderator", "Guides of the Void"]
SOFT_RED = 0xCD6D6D
STARBOARD_COLOUR = 0xFFAC33
DARK_BLUE = 0x00008B
PALE_GREEN = 0xBCF5BC
FEL_ID = 235055132843180032
DER_ID = 295553857054834690
