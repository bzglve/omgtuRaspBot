from environs import Env

env = Env()
env.read_env()

BOT_TOKEN: str = env.str("BOT_TOKEN")
SQLITE_DB_PATH: str = env.path("SQLITE_DB_PATH")
LOGLEVEL: int = env.log_level("LOGLEVEL")
