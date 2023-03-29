from environs import Env

env = Env()
env.read_env(".env")

BOT_TOKEN = env.str("BOT_TOKEN")
SQLITE_DB_PATH = env.path("SQLITE_DB_PATH")
LOGLEVEL = env.log_level("LOGLEVEL")
