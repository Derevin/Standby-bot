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

ALTER_STARBOARD = """
ALTER TABLE "starboard" ADD CONSTRAINT "starboard_fk0" FOREIGN KEY ("usr_id") REFERENCES "usr"("usr_id");
"""


async def create_tables(con):
    try:
        await con.execute(CREATE_USER)
        await con.execute(CREATE_STARBOARD)
        await con.execute(CREATE_GUILD)
        await con.execute(ALTER_USER)
        await con.execute(ALTER_STARBOARD)
    except Exception as e:
        print("expected create exception:", e)

