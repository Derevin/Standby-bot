RULES_CHANNEL_NAME = "getting-started"
BOT_SPAM_ID = 343465942199828481
GIVEAWAYS_ID = 366906148500275200
TICKET_CHANNEL_ID = 994974670275223673
RULES_MESSAGE_ID = 754461970488492032

RULES_LIST = [
    "1. Respect all other members.",
    "2. Keep conversations friendly and calm.",
    "3. No impersonating a moderator, or any others.",
    "4. No inappropriate names or avatars.",
    "5. No hate speech or slurs of any kind.",
    "6. No advertising or spam.",
    "7. No links to or posting NSFW content, including pornography, gore and sexualised lolis.",
    "8. Listen to moderators.",
    f"9. Do not appeal mod decisions in public channels - open a ticket in <#{TICKET_CHANNEL_ID}>.",
    "10. No attacking race, religion, sexual orientation, gender identity or nationality.",
    f"11. Keep bot commands in <#{BOT_SPAM_ID}> unless it's relevant to the current conversation.",
    "12. Don't ping clan roles, @here or @everyone",
]

GENERAL_INFO = f"""Talking in the server awards XP - you need Level 3 to access <#{GIVEAWAYS_ID}>.
        Enforcement of the rules is always at the moderators' discretion.
        Repeated infractions within a 30 day period lead to automatic action:
        2 Warns = Muted for a day
        3 Warns = Muted for 3 days
        4 Warns = Banned for 7 days
        5 Warns = Permanent ban"""

DELIMITERS = {"clan": "Clans", "opt-in": "Opt-in", "color": "Colors"}

PRIO_ROLES = ["UpdateSquad", "Vie for the Void"]

ROLE_DESCRIPTIONS = {
    "Offers": "News about free or discounted games in #offers",
    "UpdateSquad": "Get notified about server changes, giveaways, events, polls etc",
}
