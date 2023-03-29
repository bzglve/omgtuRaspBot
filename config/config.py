from environs import Env, EnvError

env = Env()
env.read_env(".env")

BOT_TOKEN = env.str("BOT_TOKEN")
try:
    poll_interval = env.int("POLL_INTERVAL")
except EnvError:
    poll_interval = 0.001
