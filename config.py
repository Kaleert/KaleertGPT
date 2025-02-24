BOT_TOKEN = "" #токен бота (REQUIRED)
API_ID = 12345 #(REQUIRED)
API_HASH = "" #(REQUIRED)
URL = "https://mydomain.com" #адрес сайта #(REQUIRED)
WEB_PORT = 12345 #OPTIONAL, default = 12345
system_prompt = "ты универсальный помощник" #OPTIONAL
ENGEENER_LOGS = False #OPTIONAL, default = False
BOT_USERNAME = "USER_NAME_BOT" #(REQUIRED) юз бота в Telegram (без @)
BOT_NAME = "ChatGPT" #OPTIONAL
SUBSCRIBE_REQUIRED = False #OPTIONAL, Default = False
CHANNEL = "@channel" #OPTIONAL #бот должен быть админом канала
CHECK_INTERVAL = 60 #интервал проверки подписки #OPTIONAL, default = 60

ADMIN_LOGGING = True #OPTIONAL (False) Если True группа будет получать логи от бота
BOT_LOGS_CHANNEL = -1001234567890 #OPTIONAL (REQUIRED if ADMIN_LOGGING = True)
IS_SUPERGROUP = True #REQUIRED #(False) True если канал юзера является суппергруппой, False если канал юзера является обычной группой или каналом
#OPTIONAL (REQUIRED if ADMIN_LOGGING = True)
BAN_THREAD = 3
UNBAN_THREAD = 5
ACTION_THREAD = 9
REGISTER_THREAD = 7

API_PROVIDERS = {
    "provider1": {"base_url": "http://api.povider1.fun", "api_key": "sk-...", "models": ["gpt-4o-mini", "deepseek-v3"], "proxy": None},
    "provider2": {"base_url": "http://api.povider2.fun", "api_key": "sk-...", "models": ["gpt-4", "gpt-3.5-turbo", "gpt-4o", "gpt-4o-mini"], "proxy": "http://your_proxy_address:port"} #"proxy": "socks5://your_socks5_address:port"
}

API_PROVIDERS_IMAGE = {
	"provider1": {"base_url": "http://api.povider1.fun", "api_key": "sk-...", "img_models": ["flux-dev", "flux-schnell", "sdxl-turbo", "poli"]},
	"provider2": {"base_url": "http://api.povider2.fun", "api_key": "sk-...", "img_models": ["flux"]}
}

RESOLUTIONS = {
    "1024x1024": (1024, 1024),
    "1024x576": (1024, 576),
    "1024x768": (1024, 768),
    "512x512": (512, 512),
    "576x1024": (576, 1024),
    "768x1024": (768, 1024)
}