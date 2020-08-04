import os

DEBUG = os.getenv("DEBUG", False)

if DEBUG:
    print("debug")
    from pathlib import Path
    from dotenv import load_dotenv

    env_path = Path(".") / ".env.debug"
    load_dotenv(dotenv_path=env_path)
    from settings_files.dev import *
else:
    print("prod")
    from settings_files.prod import *
