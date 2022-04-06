import asyncpg

CREATE_USER = """
CREATE TABLE IF NOT EXISTS "usr" (
    "usr_id" BIGINT NOT NULL,
    "thanks" integer NOT NULL DEFAULT '0',
    "guild_id" BIGINT NOT NULL,
    CONSTRAINT "usr_pk" PRIMARY KEY ("usr_id")
) WITH (
  OIDS=FALSE
);
"""

CREATE_STARBOARD = """CREATE TABLE IF NOT EXISTS "starboard" (
    "msg_id" BIGINT NOT NULL,
    "sb_id" BIGINT NOT NULL,
    "usr_id" BIGINT NOT NULL,
    "stars" integer NOT NULL DEFAULT '0',
    CONSTRAINT "starboard_pk" PRIMARY KEY ("msg_id")
) WITH (
  OIDS=FALSE
);
"""

CREATE_GUILD = """
CREATE TABLE IF NOT EXISTS "guild" (
    "guild_id" BIGINT NOT NULL,
    CONSTRAINT "guild_pk" PRIMARY KEY ("guild_id")
) WITH (
  OIDS=FALSE
);
"""

ALTER_USER = 'ALTER TABLE "usr" ADD CONSTRAINT "usr_fk0" FOREIGN KEY ("guild_id") REFERENCES "guild"("guild_id");'
ALTER_USER_ADD_SKULLS = 'ALTER TABLE "usr" ADD "skulls" integer DEFAULT 0'

ALTER_STARBOARD = """
ALTER TABLE "starboard" ADD CONSTRAINT "starboard_fk0" FOREIGN KEY ("usr_id") REFERENCES "usr"("usr_id");
"""


CREATE_TMERS = """
CREATE TABLE IF NOT EXISTS "tmers" (
    "tmer_id" SERIAL PRIMARY KEY,
    "usr_id" BIGINT NOT NULL,
    "expires" TIMESTAMP NOT NULL,
    "ttype" BIGINT NOT NULL,
    "params" TEXT
) WITH (
  OIDS=FALSE
);
"""

ALTER_TMERS = """
ALTER TABLE "tmers" ADD CONSTRAINT "usr_fk0" FOREIGN KEY ("usr_id") REFERENCES "usr"("usr_id");
"""


ALTER_GUILD_ADD_PERMS = """
ALTER TABLE "guild" ADD "config" TEXT;
"""

CREATE_BDAYS = """
CREATE TABLE IF NOT EXISTS "bdays" (
    "usr_id" BIGINT NOT NULL,
    "month" SMALLINT NOT NULL,
    "day" SMALLINT NOT NULL,
    CONSTRAINT "bdays_pk" PRIMARY KEY ("usr_id")
) WITH (
  OIDS=FALSE
);
"""
ALTER_BDAYS = """
ALTER TABLE "bdays" ADD CONSTRAINT "usr_fk0" FOREIGN KEY ("usr_id") REFERENCES "usr"("usr_id");
"""


async def create_tables(con):
    try:
        await con.execute(CREATE_USER)
        await con.execute(CREATE_STARBOARD)
        await con.execute(CREATE_GUILD)
        await con.execute(ALTER_USER_ADD_SKULLS)
        await con.execute(ALTER_USER)
        await con.execute(ALTER_STARBOARD)
        print("successfully ran db script batch 1")
    except Exception as e:
        print("expected create exception 1:", e)

    try:
        await con.execute(CREATE_TMERS)
        await con.execute(ALTER_TMERS)
        print("successfully ran db script batch 2")
    except Exception as e:
        print("expected create exception 2:", e)

    try:
        await con.execute(CREATE_BDAYS)
        await con.execute(ALTER_BDAYS)
        print("succesfully ran db script batch 3")
    except Exception as e:
        print("expected create exception 3:", e)
