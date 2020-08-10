import asyncpg


async def create_tables(pool):
    await pool.execute(
        """
        CREATE TABLE IF NOT EXISTS "user" (
    "user_id" integer NOT NULL,
    "thanks" integer NOT NULL DEFAULT '0',
    "guild_id" integer NOT NULL DEFAULT '0',
    CONSTRAINT "user_pk" PRIMARY KEY ("user_id")
) WITH (
  OIDS=FALSE
);

CREATE TABLE IF NOT EXISTS "starboard" (
    "msg_id" integer NOT NULL,
    "user_id" integer NOT NULL,
    "stars" integer NOT NULL DEFAULT '0',
    CONSTRAINT "starboard_pk" PRIMARY KEY ("msg_id")
) WITH (
  OIDS=FALSE
);

CREATE TABLE IF NOT EXISTS "guild" (
    "guild_id" integer NOT NULL,
    CONSTRAINT "guild_pk" PRIMARY KEY ("guild_id")
) WITH (
  OIDS=FALSE
);


ALTER TABLE "user" ADD CONSTRAINT "user_fk0" FOREIGN KEY ("guild_id") REFERENCES "guild"("guild_id");

ALTER TABLE "starboard" ADD CONSTRAINT "starboard_fk0" FOREIGN KEY ("user_id") REFERENCES "user"("user_id");
    """
    )
