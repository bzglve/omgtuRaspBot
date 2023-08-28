from environs import Env, EnvError

env = Env()
env.read_env(".env")

BOT_TOKEN = env.str("BOT_TOKEN")
SQLITE_DB_PATH = env.path("SQLITE_DB_PATH")
LOGLEVEL = env.log_level("LOGLEVEL")
try:
    poll_interval = env.int("POLL_INTERVAL")
except EnvError:
    poll_interval = 0.001

try:
    AUTHOR = env.str("AUTHOR")
except EnvError:
    AUTHOR = None
