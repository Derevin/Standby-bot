import nextcord
import re
import random

regex_songs_commands = []

#### What is love


async def what_is_love_resp(bot, message: nextcord.Message):
    await message.channel.send("*♬ Baby don't hurt me ♬*")


regex_songs_commands.append(
    ("^.{0,2}what is .?ove\\?{0,3}$", what_is_love_resp, re.M | re.I)
)


async def baby_dont_hurt_me_resp(bot, message: nextcord.Message):
    await message.channel.send("*♬ no more ♬*")


regex_songs_commands.append(
    ("^.{0,2}don'?t hurt me.{0,4}$", baby_dont_hurt_me_resp, re.M | re.I)
)

#### Sweet dreams


async def sweet_dreams_resp(bot, message: nextcord.Message):
    await message.channel.send("*♬ are made of this ♬*")


regex_songs_commands.append(
    ("^.{0,2}sweet dreams.{0,15}$", sweet_dreams_resp, re.M | re.I)
)

### pirates


async def yarr_harr_resp(bot, message: nextcord.Message):
    await message.channel.send("fiddle de dee")


regex_songs_commands.append(
    ("^.{0,2}(yarr har|yar har).{0,4}$", yarr_harr_resp, re.M | re.I)
)

### trust me


async def trust_me_resp(bot, message: nextcord.Message):
    await message.channel.send("I'm an engineer!")


regex_songs_commands.append(("^.{0,2}trust me.{0,4}$", trust_me_resp, re.M | re.I))

### kickapoo


async def long_ass_time_resp(bot, message: nextcord.Message):
    await message.channel.send("*♬ ..in a town called Kickapoo ♬*")


regex_songs_commands.append(
    ("^.{0,2}long ass? f(ucking)? time ago.{0,4}$", long_ass_time_resp, re.M | re.I)
)

### eminem


async def testing_attention_resp(bot, message: nextcord.Message):
    await message.channel.send("*♬ Feel the tension soon as someone mentions me ♬*")


regex_songs_commands.append(
    (
        "^testing,? [\"']?attention,? please!?[\"']?$",
        testing_attention_resp,
        re.M | re.I,
    )
)


async def testing_emn_resp(bot, message: nextcord.Message):
    await message.channel.send("**♬ Attention please! ♬**")


regex_songs_commands.append(("^testing.{0,4}$", testing_emn_resp, re.M | re.I))


async def spaghetti_resp(bot, message: nextcord.Message):
    await message.channel.send("*mom's spaghetti*")


regex_songs_commands.append(("^.{18,30}already\\W{0,4}$", spaghetti_resp, re.M | re.I))

#### moneyyy


async def moneyyy_resp(bot, message: nextcord.Message):
    await message.channel.send(
        "Money money money money money money money money money money!"
    )


regex_songs_commands.append(("^here comes the money.{0,4}$", moneyyy_resp, re.M | re.I))

#### yesterday


async def yesterday_resp(bot, message: nextcord.Message):
    await message.channel.send("*♬ All my troubles seemed so far away ♬*")


regex_songs_commands.append(("^.{0,2}yesterday.{0,4}$", yesterday_resp, re.M | re.I))

#### deja vu


async def deja_vu_resp(bot, message: nextcord.Message):
    await message.channel.send("*♬ I've just been in this place before ♬*")


regex_songs_commands.append(("^.{0,2}deja vu.{0,4}$", deja_vu_resp, re.M | re.I))


async def higher_on_the_street_resp(bot, message: nextcord.Message):
    await message.channel.send("*♬ And I know it's my time to go ♬*")


regex_songs_commands.append(
    ("^.{0,2}higher on the street.{0,4}$", higher_on_the_street_resp, re.M | re.I)
)
#### allstars


async def somebody_resp(bot, message: nextcord.Message):
    await message.channel.send("**BODY ONCE TOLD ME**")


regex_songs_commands.append(("^(some|.*\\Wsome\\W*)$", somebody_resp, re.M | re.I))


async def roll_me_resp(bot, message: nextcord.Message):
    await message.channel.send("**I AIN'T THE SHARPEST TOOL IN THE SHED**")


regex_songs_commands.append(
    ("\\W*the world is gonna roll me\\W*", roll_me_resp, re.M | re.I)
)

#### hard rock


async def hard_rock_resp(bot, message: nextcord.Message):
    await message.channel.send("**Hallelujah!**")


regex_songs_commands.append(
    ("^(hard rock|.*\\Whard rock\\W*)$", hard_rock_resp, re.M | re.I)
)

#### soad


async def wake_up_resp(bot, message: nextcord.Message):
    await message.channel.send("*♬ Grab a brush and put a little make up! ♬*")


regex_songs_commands.append(("^.{0,2}wake up.{0,4}$", wake_up_resp, re.M | re.I))


#### beep boop


async def beep_boop_resp(bot, message: nextcord.Message):
    await message.channel.send("I'm a robot.")


regex_songs_commands.append(("^.{0,2}beep boop.{0,4}$", beep_boop_resp, re.M | re.I))


#### that one song


async def beep_beep_resp(bot, message: nextcord.Message):
    await message.channel.send("I'm a sheep.")


regex_songs_commands.append(("^.{0,2}beep beep.{0,4}$", beep_beep_resp, re.M | re.I))


async def bark_bark_resp(bot, message: nextcord.Message):
    await message.channel.send("I'm a shark.")


regex_songs_commands.append(("^.{0,4}bark bark.{0,4}$", bark_bark_resp, re.M | re.I))


async def meow_meow_resp(bot, message: nextcord.Message):
    await message.channel.send("I'm a cow.")


regex_songs_commands.append(("^.{0,2}meow meow.{0,4}$", meow_meow_resp, re.M | re.I))


async def quack_quack_resp(bot, message: nextcord.Message):
    await message.channel.send("I'm a yak.")


regex_songs_commands.append(
    ("^.{0,2}quack quack.{0,4}$", quack_quack_resp, re.M | re.I)
)


async def dab_dab_resp(bot, message: nextcord.Message):
    await message.channel.send("I'm a crab.")


regex_songs_commands.append(("^.{0,2}dab dab.{0,4}$", dab_dab_resp, re.M | re.I))


async def float_float_resp(bot, message: nextcord.Message):
    await message.channel.send("I'm a goat.")


regex_songs_commands.append(
    (" ^.{0,2}float float.{0,4}$", float_float_resp, re.M | re.I)
)


async def screech_screech_resp(bot, message: nextcord.Message):
    await message.channel.send("I'm a leech.")


regex_songs_commands.append(
    ("^.{0,2}screech screech.{0,4}$", screech_screech_resp, re.M | re.I)
)


async def bam_bam_resp(bot, message: nextcord.Message):
    await message.channel.send("I'm a lamb.")


regex_songs_commands.append(
    ("^.{0,2}(bam bam)(slam slam).{0,4}$", bam_bam_resp, re.M | re.I)
)


async def dig_dig_resp(bot, message: nextcord.Message):
    await message.channel.send("I'm a pig.")


regex_songs_commands.append(("^.{0,2}dig dig.{0,4}$", dig_dig_resp, re.M | re.I))


async def roar_roar_resp(bot, message: nextcord.Message):
    await message.channel.send(
        "I'm a boar." if 1 == random.randint(0, 1) else "Dinosaur"
    )


regex_songs_commands.append(("^.{0,2}roar roar.{0,4}$", roar_roar_resp, re.M | re.I))


async def shake_shake_resp(bot, message: nextcord.Message):
    await message.channel.send("I'm a snake.")


regex_songs_commands.append(
    ("^.{0,2}shake shake.{0,4}$", shake_shake_resp, re.M | re.I)
)


async def swish_swish_resp(bot, message: nextcord.Message):
    await message.channel.send("I'm a fish.")


regex_songs_commands.append(
    ("^.{0,2}swish swish.{0,4}$", swish_swish_resp, re.M | re.I)
)


async def squawk_squawk_resp(bot, message: nextcord.Message):
    await message.channel.send("I'm a hawk.")


regex_songs_commands.append(
    ("^.{0,2}squawk squawk.{0,4}$", swish_swish_resp, re.M | re.I)
)


async def cluck_cluck_resp(bot, message: nextcord.Message):
    await message.channel.send("I'm a duck.")


regex_songs_commands.append((".{0,2}cluck cluck.{0,4}$", cluck_cluck_resp, re.M | re.I))


async def growl_growl_resp(bot, message: nextcord.Message):
    await message.channel.send("I'm an owl.")


regex_songs_commands.append(
    ("^.{0,2}growl growl.{0,4}$", growl_growl_resp, re.M | re.I)
)


async def drop_drop_resp(bot, message: nextcord.Message):
    await message.channel.send("Do the flop!")


regex_songs_commands.append(("^.{0,2}drop drop.{0,4}$", drop_drop_resp, re.M | re.I))


async def boink_boink_resp(bot, message: nextcord.Message):
    await message.channel.send("I'm bad at rhyming. :(")


regex_songs_commands.append(
    ("^.{0,2}boink boink.{0,4}$", boink_boink_resp, re.M | re.I)
)


async def click_click_resp(bot, message: nextcord.Message):
    await message.channel.send("I'm a chick.")


regex_songs_commands.append(
    ("^.{0,2}click click.{0,4}$", click_click_resp, re.M | re.I)
)


async def blue_resp(bot, message: nextcord.Message):
    await message.channel.send("♬ Da ba dee da ba di ♬")


regex_songs_commands.append(("^.{0,2}I('| a)?m blue{0,4}$", blue_resp, re.M | re.I))
