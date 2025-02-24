
import random
import secrets
from flask import Flask, flash, redirect, request, jsonify, render_template, session
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
import uuid
import requests
import asyncio
import logging
import traceback
import os
import re
import time
import signal
import aiohttp
from datetime import datetime, timedelta
from pyrogram import Client, errors
import markdown2
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.enums.chat_member_status import ChatMemberStatus
from aiogram.enums.parse_mode import ParseMode
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command, BaseFilter, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from openai import OpenAIError
from typing import Dict, List, Optional, Tuple, Union
import aiosqlite
import config
from config import *
import sqlite3
import bleach
import json
from bs4 import BeautifulSoup
import threading

def startup():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    
    global WEB_PORT, system_prompt, ENGEENER_LOGS, SUBSCRIBE_REQUIRED, CHECK_INTERVAL, ADMIN_LOGGING, BOT_NAME, BOT_LOGS_CHANNEL, BAN_THREAD, UNBAN_THREAD, ACTION_THREAD, REGISTER_THREAD

    try:
        BOT_TOKEN
        bot_token_exists = True
    except NameError:
        bot_token_exists = False
    if not bot_token_exists:
        logging.error("BOT_TOKEN не указан в config!")
        exit()
    elif not isinstance(BOT_TOKEN, str) or not BOT_TOKEN:
        logging.error("BOT_TOKEN указан неверно!")
        exit()

    try:
        API_ID
        api_id_exists = True
    except NameError:
        api_id_exists = False
    if not api_id_exists:
        logging.error("API_ID не указан в config!")
        exit()
    elif not isinstance(API_ID, int) or API_ID <= 0:
        logging.error("API_ID указан неверно!")
        exit()
        
    try:
        API_HASH
        api_hash_exists = True
    except:
        api_hash_exists = False
    if not api_hash_exists:
        logging.error("API_HASH не указан в config!")
        exit()        
    elif not isinstance(API_HASH, str) or not API_HASH:
        logging.error("API_HASH не указан или указан неверно!")
        exit()

    try:
        URL
        url_exists = True
    except NameError:
        url_exists = False
    if not url_exists:
        logging.error("URL не указан в config!")
        exit()
    elif not isinstance(URL, str) or not URL:
        logging.error("URL указан неверно!")
        exit()

    try:
        CHANNEL
        channel_exists = True
    except NameError:
        channel_exists = False
    if not channel_exists:
        logging.error("CHANNEL не указан в config, выключаем SUBSCRIBE_REQUIRED...")
        SUBSCRIBE_REQUIRED = False
    elif not isinstance(CHANNEL, str) or not CHANNEL:
        logging.error("CHANNEL указан неверно, выключаем SUBSCRIBE_REQUIRED...")
        SUBSCRIBE_REQUIRED = False

    try:
        BOT_USERNAME
        bot_username_exists = True
    except:
        bot_username_exists = False
    if not bot_username_exists:
        logging.error("BOT_USERNAME не указан в config!")
        exit()        
    elif not isinstance(BOT_USERNAME, str) or not BOT_USERNAME:
        logging.error("BOT_USERNAME не указан или указан неверно!")
        exit()

    try:
        BOT_NAME
        bot_name_exists = True
    except:
        bot_name_exists = False
    if not bot_name_exists:
        logging.error("BOT_NAME не указан в config, использую значение по умолчанию...")
        BOT_NAME = "ChatGPT"
    elif not isinstance(BOT_NAME, str) or not BOT_NAME:
        logging.error("BOT_RNAME не указан или указан неверно, использую значение по умолчанию...")
        BOT_NAME = "ChatGPT"
    # WEB_PORT
    try:
        WEB_PORT  # Пытаемся получить доступ к переменной
        port_exists = True
    except NameError:
        port_exists = False
    if not port_exists:
        logging.warning("WEB_PORT не указан в config, использую значение по умолчанию...")
        WEB_PORT = 12345  # Присваиваем значение по умолчанию
        logging.info(f"WEB_PORT установлен в значение: {WEB_PORT}")
    elif not isinstance(WEB_PORT, int) or WEB_PORT <= 0:
        logging.error("WEB_PORT указан неверно, использую значение по умолчанию...")
        WEB_PORT = 12345
        logging.info(f"WEB_PORT установлен в значение: {WEB_PORT}")

    # system_prompt
    try:
        system_prompt  # Пытаемся получить доступ к переменной
        prompt_exists = True
    except NameError:
        prompt_exists = False
    if not prompt_exists:
        logging.warning("system_prompt не указан в config, использую значение по умолчанию...")
        system_prompt = getattr(config, 'system_prompt', "Ты универсальный помощник.")
        logging.info(f"system_prompt установлен в значение: {system_prompt}")
    elif not isinstance(system_prompt, str) or not system_prompt:
        logging.error("system_prompt указан неверно, использую значение по умолчанию...")
        system_prompt = "Ты универсальный помощник."
        logging.info(f"system_prompt установлен в значение: {system_prompt}")

    # ENGEENER_LOGS
    try:
        ENGEENER_LOGS  # Пытаемся получить доступ к переменной
        logs_exists = True
    except NameError:
        logs_exists = False
    if not logs_exists:
        logging.warning("ENGEENER_LOGS не указан в config, использую значение по умолчанию...")
        ENGEENER_LOGS = getattr(config, 'ENGEENER_LOGS', False)
        logging.info(f"ENGEENER_LOGS установлен в значение: {ENGEENER_LOGS}")
    elif not isinstance(ENGEENER_LOGS, bool) and ENGEENER_LOGS is not None:
        logging.error("ENGEENER_LOGS указан неверно, использую значение по умолчанию...")
        ENGEENER_LOGS = False
        logging.info(f"ENGEENER_LOGS установлен в значение: {ENGEENER_LOGS}")

    # SUBSCRIBE_REQUIRED
    try:
        SUBSCRIBE_REQUIRED  # Пытаемся получить доступ к переменной
        subscribe_exists = True
    except NameError:
        subscribe_exists = False
    if not subscribe_exists:
        logging.warning("SUBSCRIBE_REQUIRED не указан в config, использую значение по умолчанию...")
        SUBSCRIBE_REQUIRED = getattr(config, 'SUBSCRIBE_REQUIRED', False)
        logging.info(f"SUBSCRIBE_REQUIRED установлен в значение: {SUBSCRIBE_REQUIRED}")
    elif not isinstance(SUBSCRIBE_REQUIRED, bool) and SUBSCRIBE_REQUIRED is not None:
        logging.error("SUBSCRIBE_REQUIRED указан неверно, использую значение по умолчанию...")
        SUBSCRIBE_REQUIRED = False
        logging.info(f"SUBSCRIBE_REQUIRED установлен в значение: {SUBSCRIBE_REQUIRED}")

    # CHECK_INTERVAL
    try:
        CHECK_INTERVAL  # Пытаемся получить доступ к переменной
        interval_exists = True
    except NameError:
        interval_exists = False
    if not interval_exists:
        logging.warning("CHECK_INTERVAL не указан в config, использую значение по умолчанию...")
        CHECK_INTERVAL = getattr(config, 'CHECK_INTERVAL', 60)
        logging.info(f"CHECK_INTERVAL установлен в значение: {CHECK_INTERVAL}")
    elif not isinstance(CHECK_INTERVAL, int) or CHECK_INTERVAL <= 0:
        logging.error("CHECK_INTERVAL указан неверно, использую значение по умолчанию...")
        CHECK_INTERVAL = 60
        logging.info(f"CHECK_INTERVAL установлен в значение: {CHECK_INTERVAL}")

    try:
        BOT_LOGS_CHANNEL
        bot_logs_channel_exists = True
    except NameError:
        bot_logs_channel_exists = False
    if not bot_logs_channel_exists:
        logging.error("BOT_LOGS_CHANNEL не указан в config, выключаем ADMIN_LOGGING...")
        ADMIN_LOGGING = False
    elif not isinstance(BOT_LOGS_CHANNEL, int) or not BOT_LOGS_CHANNEL:
        logging.error("BOT_LOGS_CHANNEL указан неверно, выключаем ADMIN_LOGGING...")
        ADMIN_LOGGING = False

    try:
        IS_SUPERGROUP
        is_supergroup_exists = True
    except NameError:
        is_supergroup_exists = False
    if not is_supergroup_exists:
        logging.error("IS_SUPERGROUP не указан в config, выключаем ADMIN_LOGGING...")
        ADMIN_LOGGING = False
    elif not isinstance(IS_SUPERGROUP, bool) or not IS_SUPERGROUP:
        logging.error("IS_SUPERGROUP указан неверно, выключаем ADMIN_LOGGING...")
        ADMIN_LOGGING = False

    try:
        ADMIN_LOGGING
        admin_logging_exists = True
    except NameError:
        admin_logging_exists = False
    if not admin_logging_exists:
        logging.warning("ADMIN_LOGGING не указан в config, использую значение по умолчанию...")
        ADMIN_LOGGING = getattr(config, 'ADMIN_LOGGING', False)
        logging.info(f"ADMIN_LOGGING установлен в значение: {ADMIN_LOGGING}")
    elif not isinstance(ADMIN_LOGGING, bool):  # Исправлено на bool
        logging.error("ADMIN_LOGGING не указан или указан неверно, выключаем...")
        ADMIN_LOGGING = False

    try:
        BAN_THREAD
        ban_thread_exists = True
    except NameError:
        ban_thread_exists = False
    if not ban_thread_exists:
        logging.error("BAN_THREAD не указан в config, выключаем ADMIN_LOGGING...")
        BAN_THREAD = None
        ADMIN_LOGGING = False
    elif ADMIN_LOGGING and IS_SUPERGROUP and (not isinstance(BAN_THREAD, int) or BAN_THREAD == None or BAN_THREAD <= 0):  #Проверяем ADMIN_LOGGING перед проверкой потоков
        logging.error("BAN_THREAD указан неверно, Выключаем ADMIN_LOGGING...")
        ADMIN_LOGGING = False
        BAN_THREAD = None

    try:
        UNBAN_THREAD
        unban_thread_exists = True
    except NameError:
        unban_thread_exists = False
    if not unban_thread_exists:
        logging.error("UNBAN_THREAD не указан в config, выключаем ADMIN_LOGGING...")
        ADMIN_LOGGING = False
        UNBAN_THREAD = None
    elif ADMIN_LOGGING and IS_SUPERGROUP and (not isinstance(UNBAN_THREAD, int) or UNBAN_THREAD == None or UNBAN_THREAD <= 0):  #Проверяем ADMIN_LOGGING перед проверкой потоков
        logging.error("UNBAN_THREAD указан неверно, Выключаем ADMIN_LOGGING...")
        ADMIN_LOGGING = False
        UNBAN_THREAD = None

    try:
        ACTION_THREAD
        action_thread_exists = True
    except NameError:
        action_thread_exists = False
    if not action_thread_exists:
        logging.error("ACTION_THREAD не указан в config, выключаем ADMIN_LOGGING...")
        ADMIN_LOGGING = False
        ACTION_THREAD = None
    elif ADMIN_LOGGING and IS_SUPERGROUP and (not isinstance(ACTION_THREAD, int) or ACTION_THREAD == None or ACTION_THREAD <= 0):  #Проверяем ADMIN_LOGGING перед проверкой потоков
        logging.error("ACTION_THREAD указан неверно, Выключаем ADMIN_LOGGING...")
        ADMIN_LOGGING = False
        ACTION_THREAD = None

    try:
        REGISTER_THREAD
        register_thread_exists = True
    except:
        register_thread_exists = False
    if not register_thread_exists:
        logging.error("REGISTER_THREAD не указан в config, выключаем ADMIN_LOGGING...")
        ADMIN_LOGGING = False
        ACTION_THREAD = None
    elif ADMIN_LOGGING and IS_SUPERGROUP and (not isinstance(REGISTER_THREAD, int)  or REGISTER_THREAD == None or REGISTER_THREAD <= 0):  #Проверяем ADMIN_LOGGING перед проверкой потоков
        logging.error("REGISTER_THREAD не указан или указан неверно, Выключаем ADMIN_LOGGING...")
        ADMIN_LOGGING = False
        REGISTER_THREAD = None
    elif not validate_api_providers(API_PROVIDERS):
        logging.error("API_PROVIDERS не валиден.")
        exit()
    elif not validate_api_providers(API_PROVIDERS_IMAGE, api_type="image"):
        logging.error("API_PROVIDERS_IMAGE не валиден.")
        exit()
    elif not validate_resolutions(RESOLUTIONS):
        logging.error("RESOLUTIONS не валиден.")
        exit()
    else:
        logging.info("CONFIG.PY в порядке, начинаю запуск...")

    main_thread()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')

app = Flask(__name__)
app.static_folder = 'static'
db_path_responses = 'responses.db'

SERVER_URL = f"{URL}:{WEB_PORT}/add_response"
ALLOWED_TAGS = ['a', 'b', 'br', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'p', 'pre', 'strong', 'ul']
ALLOWED_ATTRIBUTES = {'a': ['href', 'target', 'rel']}
pyrogram_client = Client(BOT_USERNAME, api_id=API_ID, api_hash=API_HASH)
database_lock = asyncio.Lock()
app.secret_key = secrets.token_hex(24)
file_lock = asyncio.Lock()
back_txt = "🔙 назад"
user_queues = {}
user_tasks = {}
user_locks = {}
user_first_message = {}  # Словарь для отслеживания первого сообщения пользователя
# Словарь для хранения данных о попытках входа и блокировке
login_attempts = {}
user_locks = {}  # Словарь для хранения блокировок для каждого пользователя
TIMEOUT_SECONDS = 10
user_subscription_cache = {}  # Словарь для хранения кэшированных результатов
TYPING_DELAY = 0.1
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
router = Router()
ALLOWED_TAGS = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'b', 'i', 'strong', 'em', 'tt', 'p', 'br',
                'span', 'div', 'blockquote', 'code', 'pre', 'hr', 'ul', 'ol', 'li', 'dd', 'dt',
                'img', 'a', 'sub', 'sup']
ALLOWED_ATTRIBUTES = {
    '*': ['id', 'class'],
    'a': ['href', 'alt', 'title'],
    'img': ['src', 'alt', 'title']
}

image_generation_semaphore = asyncio.Semaphore(1)

async def init_db(db_path_responses):
    async with aiosqlite.connect(db_path_responses) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS responses (
                id TEXT PRIMARY KEY,
                title TEXT,
                text TEXT
            )
        ''')
        
                # Создаем таблицу шейров
        await db.execute('''CREATE TABLE IF NOT EXISTS shares (
            id TEXT PRIMARY KEY,
            title TEXT,
            text TEXT,
            is_public INTEGER DEFAULT 0
        )''')
        await db.commit()

async def get_registered_users(db_file='bot_data.db'):
    try:
        async with aiosqlite.connect(db_file) as db:
            async with db.execute("SELECT user_id, username FROM users") as cursor:
                users = await cursor.fetchall()
                return {str(user_id): username for user_id, username in users}
    except Exception as e:
        logging.exception(f"Ошибка при получении пользователей: {e}")
        return {}
    
async def get_user_id_web(user_input, pyrogram_client):
    if ENGEENER_LOGS:
        logging.debug(f"get_user_id_web called with user_input: {user_input}")
    try:
        user_input_lower = user_input.lower()

        # Проверка на ID
        if user_input_lower.isdigit():  # Если это ID, вернуть его как число
            user_id = int(user_input_lower)
            if ENGEENER_LOGS:
                logging.debug(f"User ID received directly: {user_id}")
            return user_id

        # Проверка на юзернейм
        elif user_input_lower.startswith('@'):
            username = user_input_lower[1:]  # Удаляем '@'
        else:
            username = user_input_lower
        if ENGEENER_LOGS:
            logging.debug(f"Searching for username: {username} in database")

        # Ищем юзернейм в базе данных
        result = await execute_query_single('bot_data.db', "SELECT user_id FROM users WHERE LOWER(username) = ?", (username,))
        if result:
            user_id = result[0]
            if ENGEENER_LOGS:
                logging.debug(f"User ID found in database: {user_id}")
            return user_id
        
        if ENGEENER_LOGS:
        # Если не нашли в базе данных, ищем через Pyrogram
            logging.debug(f"User not found in database, querying Pyrogram for username: {username}")
        async with pyrogram_client:
            try:
                user = await pyrogram_client.get_users(username)
                if user:
                    user_id = user.id
                    if ENGEENER_LOGS:
                        logging.debug(f"User ID received from Pyrogram: {user_id}")
                    return user_id
            except errors.UsernameNotOccupied:
                logging.warning(f"Username '{username}' is not occupied.")
            except errors.UsernameInvalid:
                logging.warning(f"Invalid username '{username}'.")
            except Exception as e:
                logging.exception(f"Unexpected error: {e}")
        if ENGEENER_LOGS:
            logging.debug("User ID not found from any sources")
        return None

    except Exception as e:
        logging.exception(f"Error in get_user_id_web: {e}")
        return None
    
async def send_telegram_code(user_id, code):
    # тут будет отправка кода через telegram bot api
    if ENGEENER_LOGS:
        logging.info(f"Отправлен код {code} для пользователя {user_id}")
    try:
      async with Bot(token=BOT_TOKEN) as bot:
        await bot.send_message(chat_id=user_id, text="Для входа на сайт под вашим именем был запрошен код:\n" + str(code) + "\n**НИКОМУ ЕГО НЕ СООБЩАЙТЕ!**", parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
            logging.error(f"Ошибка при отправке в Telegram: {e}")

@app.route('/')
async def index():
    user_id = session.get('user_id')
    authorizated = True
    if not user_id:
        authorizated = False
    # Загрузка данных о пользователе из базы данных
    user_data = await get_user_data(user_id)
     # Генерация JavaScript-кода для регистрации языков
    languages_dir = os.path.join(app.static_folder, 'highlight', 'languages')
    languages_js = ""
    for filename in os.listdir(languages_dir):
        if filename.endswith(".min.js"):
            language_name = os.path.splitext(filename)[0]
            languages_js += f"if(hljs.getLanguage('{language_name}')){{ hljs.registerLanguage('{language_name}', hljs.getLanguage('{language_name}')); }}\n"
    return render_template('main.html', bot_username=f"{BOT_USERNAME}_bot", languages_js=languages_js, user_data=user_data, authorizated=authorizated, BOT_USERNAME=BOT_USERNAME, BOT_NAME=BOT_NAME)

async def execute_query_single(db_file, query, params=()):
    if ENGEENER_LOGS:
        logging.debug(f"Executing query: {query} with params: {params}")
    result = await execute_query(db_file, query, params)
    if ENGEENER_LOGS:
        logging.debug(f"Query result: {result}")
    if result:
        return result[0]
    return None

@app.route('/login', methods=['GET', 'POST'])
async def login():
    if 'user_id' in session:
        flash("Вы уже вошли в систему. Перейдите в свой профиль.")
        return redirect('/profile')

    error_message = None
    code_requested = 'user_session' in session

    registered_users = await get_registered_users()
    if ENGEENER_LOGS:
        logging.info(f"Зарегистрированные пользователи: {registered_users}")

    if request.method == 'POST':
        if code_requested:
            # Проверка введенного пользователем кода
            entered_code = request.form.get('code')
            session_code = session['user_session']['code']

            if entered_code == session_code:
                if time.time() - session['user_session']['timestamp'] <= 180:
                    session['user_id'] = session['user_session']['user_id']  # Сохраняем user_id в сессии
                    session.permanent = True  # Делаем сессию постоянной
                    session.pop('user_session')
                    return redirect('/profile')  # Перенаправляем на страницу профиля
                else:
                    error_message = "Код устарел. Пожалуйста, запросите новый."
            else:
                error_message = "Неверный код. Попробуйте снова."
        else:
            # Если код не был запрошен, обрабатываем ввод ID или юзернейма
            user_input = request.form.get('user_id')

            if not user_input:
                error_message = "Пожалуйста, введите ID или юзернейм."
            else:
                if ENGEENER_LOGS:
                    logging.info(f"Пользователь ввел: {user_input}")

                if user_input.isdigit() or user_input in registered_users.values():
                    if ENGEENER_LOGS:
                        logging.info("Пользователь найден.")

                    user_id = await get_user_id_web(user_input, bot)
                    if ENGEENER_LOGS:
                        logging.info(f"Полученный user_id: {user_id}")

                    if user_id:
                        code = str(random.randint(100000, 999999))
                        session['user_session'] = {'code': code, 'timestamp': time.time(), 'user_id': user_id}
                        if ENGEENER_LOGS:
                            logging.info(f"Отправка кода {code} пользователю {user_id}")
                        await send_telegram_code(user_id, code)
                        flash("Код отправлен в Telegram. Проверьте ваш чат.")
                        code_requested = True
                    else:
                        error_message = "Неверный ID или юзернейм."
                        if ENGEENER_LOGS:
                            logging.warning(f"Не удалось получить user_id для: {user_input}")
                else:
                    error_message = "ID или юзернейм не найдены."
                    if ENGEENER_LOGS:
                        logging.warning(f"Пользователь не найден: {user_input}")

    return render_template('login.html', error_message=error_message, code_requested=code_requested, BOT_USERNAME=BOT_USERNAME, BOT_NAME=BOT_NAME)

def update_login_attempts(user_input):
    now = time.time()
    if user_input not in login_attempts:
        login_attempts[user_input] = {'attempts': 3, 'delay': 0, 'last_attempt': now}

    attempts_data = login_attempts[user_input]
    if now - attempts_data['last_attempt'] > attempts_data['delay']:
        attempts_data['attempts'] = 3
        attempts_data['delay'] = 0

    attempts_data['last_attempt'] = now

    if attempts_data['attempts'] > 0:
        attempts_data['attempts'] -= 1
    else:
        if attempts_data['delay'] == 0:
            attempts_data['delay'] = 300
        else:
            attempts_data['delay'] *= 2

    return attempts_data['attempts'], attempts_data['delay']

@app.route('/profile', methods=['GET'])
async def profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    # Загрузка данных о пользователе из базы данных
    user_data = await get_user_data(user_id)
    if not user_data:
        flash("Профиль не найден!")
        return redirect('/login')

    return render_template('profile.html', user_data=user_data)

async def get_user_data(user_id):
    result = await execute_query_single('bot_data.db', "SELECT username, first_name, last_name FROM users WHERE user_id = ?", (user_id,))
    if result:
        return {
            'username': result[0],
            'first_name': result[1],
            'last_name': result[2]
        }
    else:
        return None

@app.route('/contacts')
async def contacts():
    user = session.get('user')
    # Генерация JavaScript-кода для регистрации языков
    languages_dir = os.path.join(app.static_folder, 'highlight', 'languages')
    languages_js = ""
    for filename in os.listdir(languages_dir):
        if filename.endswith(".min.js"):
            language_name = os.path.splitext(filename)[0]
            languages_js += f"if(hljs.getLanguage('{language_name}')){{ hljs.registerLanguage('{language_name}', hljs.getLanguage('{language_name}')); }}\n"
    return render_template('contacts.html', bot_username=BOT_USERNAME, languages_js=languages_js, user=user, BOT_USERNAME=BOT_USERNAME, BOT_NAME=BOT_NAME)

@app.route('/support')
async def support():
    user = session.get('user')
      # Генерация JavaScript-кода для регистрации языков
    languages_dir = os.path.join(app.static_folder, 'highlight', 'languages')
    languages_js = ""
    for filename in os.listdir(languages_dir):
        if filename.endswith(".min.js"):
            language_name = os.path.splitext(filename)[0]
            languages_js += f"if(hljs.getLanguage('{language_name}')){{ hljs.registerLanguage('{language_name}', hljs.getLanguage('{language_name}')); }}\n"
    return render_template('support.html', bot_username=BOT_USERNAME, languages_js=languages_js, user=user, BOT_NAME=BOT_NAME)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash("Вы вышли из профиля.")
    return redirect('/')

@app.route('/stats')
async def get_stats():
    try:
        start_time = datetime.now() - timedelta(days=2)  # Замените на ваш способ получения времени запуска бота
        uptime = datetime.now() - start_time
        uptime_str = str(uptime).split('.')[0]
        # Подсчет уникальных моделей
        unique_models = set()
        for provider in API_PROVIDERS.values():
            unique_models.update(provider["models"])

        # Выводим уникальные модели в консоль для проверки
        if ENGEENER_LOGS:
            logging.info(f"Уникальные модели: {unique_models}")

        model_count = len(unique_models)  # Количество уникальных моделей

        total_responses = await execute_query_single('bot_data.db', "SELECT SUM(requests_count) FROM user_profile")
        total_responses = total_responses[0] if total_responses and total_responses[0] else 0
        user_count = await execute_query_single('bot_data.db', "SELECT COUNT(*) FROM users")
        user_count = user_count[0] if user_count and user_count[0] else 0
        approx_message_count = (await execute_query_single('_history.db', "SELECT COUNT(*) FROM messages"))
        approx_message_count = approx_message_count[0] // 2 if approx_message_count and approx_message_count[0] else 0
        stats_data = {
            "uptime": uptime_str,
            "model_count": model_count,
            "total_responses": total_responses,
            "user_count": user_count,
            "approx_message_count": total_responses
        }
        return jsonify(stats_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

        
@app.route('/add_response', methods=['POST'])
async def add_response():
    data = request.get_json()
    title = data.get('title')
    text = data.get('text')
    response_id = str(uuid.uuid4())

    async with aiosqlite.connect(db_path_responses) as db:
        await db.execute("INSERT INTO responses (id, title, text) VALUES (?, ?, ?)", (response_id, title, text))
        await db.commit()

    return jsonify({"response_id": response_id}), 200


@app.route('/response/<response_id>')
async def get_response(response_id):
    try:
        async with aiosqlite.connect(db_path_responses) as db:
            async with db.execute("SELECT title, text FROM responses WHERE id = ?", (response_id,)) as cursor:
                result = await cursor.fetchone()
                title, text = result if result else ("Ответ не найден", "Ответ не найден")

                # Разбиваем текст на части до и после блоков кода
                parts = text.split('```')
                highlighted_text = ""

                for i, part in enumerate(parts):
                    if i % 2 == 0:  # Текст вне кода
                        highlighted_text += part
                    else:  # Блок кода
                        lines = part.splitlines()
                        if lines:
                            language = lines[0].strip()
                            code = "\n".join(lines[1:])  # удаляем первую строку (язык)
                            try:
                                lexer = get_lexer_by_name(language)
                                formatter = HtmlFormatter()
                                highlighted_code = highlight(code, lexer, formatter)
                                highlighted_text += f"<pre><code class='language-{language}'>{highlighted_code}</code></pre>"
                            except Exception as e:
                                highlighted_text += f"<pre><code>{code}</code></pre>"  # ошибка при подсветке - отображаем без подсветки

                cleaned_html = bleach.clean(highlighted_text, tags=ALLOWED_TAGS + ['pre', 'code'], attributes=ALLOWED_ATTRIBUTES, strip=True)

                # Генерация JavaScript-кода для регистрации языков
                languages_dir = os.path.join(app.static_folder, 'highlight', 'languages')
                languages_js = ""
                for filename in os.listdir(languages_dir):
                    if filename.endswith(".min.js"):
                        language_name = os.path.splitext(filename)[0]
                        languages_js += f"if(hljs.getLanguage('{language_name}')){{ hljs.registerLanguage('{language_name}', hljs.getLanguage('{language_name}')); }}\n"

                mobile = request.args.get('mobile')
                if mobile == 'true':
                    return render_template('response_mobile.html', title=title, response_text=cleaned_html, response_id=response_id, languages_js=languages_js, BOT_USERNAME=BOT_USERNAME, BOT_NAME=BOT_NAME)
                else:
                    return render_template('response.html', title=title, response_text=cleaned_html, response_id=response_id, languages_js=languages_js, BOT_USERNAME=BOT_USERNAME, BOT_NAME=BOT_NAME)
    except Exception as e:
        return f"Ошибка: {e}", 500

def signal_handler(sig, frame):
    print('SYS_INFO: Выключение бота...')
    asyncio.run(shutdown())  # Вызываем функцию shutdown()

async def shutdown():
    print("Закрытие ресурсов...")
    if pyrogram_client:
        asyncio.create_task(pyrogram_client.stop()) # Запускаем асинхронно
        
    for task in user_tasks.values():
            task.cancel()
    await asyncio.gather(*user_tasks.values(), return_exceptions=True) # Дождемся завершения или отмены всех задач
        
    await bot.session.close()
    print("Выключение завершено.")
    exit(0)


async def check_authorization(client):
    try:
        await client.get_me()
        print("Pyrogram client is authorized.")
        return True
    except errors.AuthKeyInvalid as e:
        print(f"Pyrogram client is NOT authorized: {e}")
        return False
    except errors.RPCError as e:
        print(f"Pyrogram RPC error: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

async def create_database(db_file):
    db_file_path = os.path.abspath(db_file)
    os.makedirs(os.path.dirname(db_file_path), exist_ok=True)
    try:
        async with aiosqlite.connect(db_file_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS channel_status (
                    user_id INTEGER PRIMARY KEY,
                    subscribed INTEGER DEFAULT 0,
                    last_check INTEGER DEFAULT 0
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS admins (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    level INTEGER DEFAULT 1
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS banned_users (
                    user_id INTEGER PRIMARY KEY,
                    ban_until INTEGER,
                    ban_reason TEXT,
                    banned_by INTEGER
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS ban_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    banned_by INTEGER,
                    ban_until INTEGER,
                    ban_reason TEXT,
                    timestamp INTEGER
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS broadcasts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    text TEXT,
                    media_type TEXT,
                    media_id TEXT,
                    enabled BOOLEAN DEFAULT 0,
                    scheduled_time TEXT,
                    creation_date TEXT,
                    sent INTEGER DEFAULT 0,
                    successful INTEGER DEFAULT 0,
                    failed INTEGER DEFAULT 0,
                    failed_user_ids TEXT
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT DEFAULT '',
                    first_name TEXT DEFAULT '',
                    last_name TEXT DEFAULT ''
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_profile (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT DEFAULT '',
                    model TEXT DEFAULT "gpt-4o",
                    img_model TEXT DEFAULT "flux",
                    balance INTEGER DEFAULT 0,
                    referrals INTEGER DEFAULT 0,
                    last_seen INTEGER DEFAULT 0,
                    invited_by INTEGER DEFAULT NULL,
                    requests_count INTEGER DEFAULT 0
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    user_id INTEGER,
                    role TEXT,
                    message TEXT
                )
            ''')
            await db.commit()
        return True
    except Exception as e:
        logging.exception(f"Ошибка при создании базы данных {db_file}: {e}")
        return False

async def execute_query_single(db_file, query, params=()):
    if ENGEENER_LOGS:
        logging.debug(f"Executing query: {query} with params: {params}")
    result = await execute_query(db_file, query, params)
    if ENGEENER_LOGS:
        logging.debug(f"Query result: {result}")
    if result:
        try:
            if ENGEENER_LOGS:
                logging.debug(f"Type of result: {type(result)}")
            return result[0]
        except IndexError:
            logging.error(f"IndexError: list index out of range")
            return None
    else:
        return None
    
async def execute_query(db_file, query, params=()):
    if ENGEENER_LOGS:
        logging.debug(f"Executing query: {query} with params: {params}") #добавлен лог
    try:
        async with aiosqlite.connect(db_file) as db:
            async with db.cursor() as cursor:
                await cursor.execute(query, params)
                result = await cursor.fetchall()
                if ENGEENER_LOGS:
                    logging.debug(f"Query result: {result}") #добавлен лог
                return result
    except Exception as e:
        logging.exception(f"Ошибка SQL: {e}")
        return None

async def execute_update(db_file, query, params=()):
    try:
        async with aiosqlite.connect(db_file) as db:
            async with db.cursor() as cursor:
                await cursor.execute(query, params)
                await db.commit()
                if ENGEENER_LOGS:
                    logging.info(f"Успешно выполнен запрос: {query} с параметрами {params}")
                return True
    except Exception as e:
        logging.exception(f"Ошибка SQL в запросе {query} с параметрами {params}: {e}")
        return False
       
async def get_user_referral_count(user_id):
    result = await execute_query_single('bot_data.db', "SELECT referrals FROM user_profile WHERE user_id = ?", (user_id,))
    return result[0] if result else 0

def validate_api_providers(api_providers: Dict[str, Dict[str, Union[str, List[str]]]], api_type: str = "text") -> bool:
    if not isinstance(api_providers, dict):
        logging.error(f"API_PROVIDERS ({api_type}) должен быть словарем.")
        return False

    for provider_name, provider_config in api_providers.items():
        if not isinstance(provider_name, str):
            logging.error(f"Имя провайдера должно быть строкой. Найдено: {provider_name}")
            return False

        if not isinstance(provider_config, dict):
            logging.error(f"Конфигурация для провайдера '{provider_name}' должна быть словарем.")
            return False

        if "base_url" not in provider_config:
            logging.error(f"У провайдера '{provider_name}' отсутствует 'base_url'.")
            return False
        if not isinstance(provider_config["base_url"], str) or not provider_config["base_url"].startswith("http"):
            logging.error(f"У провайдера '{provider_name}' неверный 'base_url': {provider_config['base_url']}")
            return False

        if "api_key" not in provider_config:
            logging.error(f"У провайдера '{provider_name}' отсутствует 'api_key'.")
            return False
        if not isinstance(provider_config["api_key"], str):
            logging.error(f"У провайдера '{provider_name}' неверный 'api_key': {provider_config['api_key']}")
            return False

        models_key = "models" if api_type == "text" else "img_models"
        if models_key not in provider_config:
            logging.error(f"У провайдера '{provider_name}' отсутствует '{models_key}'.")
            return False
        if not isinstance(provider_config[models_key], list):
            logging.error(f"У провайдера '{provider_name}' неверный '{models_key}': должен быть списком.")
            return False
        if not all(isinstance(model, str) for model in provider_config[models_key]):
            logging.error(f"У провайдера '{provider_name}' неверный '{models_key}': все элементы должны быть строками.")
            return False  # тут ошибка
        if not provider_config[models_key]:  # Check for empty list
            logging.error(f"У провайдера '{provider_name}' пустой список '{models_key}'.")
            return False

    return True

def validate_resolutions(resolutions: Dict[str, Tuple[int, int]]) -> bool:
    """Проверяет словарь RESOLUTIONS."""

    if not isinstance(resolutions, dict):
        logging.error("RESOLUTIONS должен быть словарем.")
        return False

    for resolution_name, resolution_tuple in resolutions.items():
        if not isinstance(resolution_name, str):
            logging.error(f"Имя разрешения должно быть строкой. Найдено: {resolution_name}")
            return False

        if not isinstance(resolution_tuple, tuple):
            logging.error(f"Разрешение '{resolution_name}' должно быть кортежем.")
            return False

        if len(resolution_tuple) != 2:
            logging.error(f"Разрешение '{resolution_name}' должно содержать ровно два элемента (ширина, высота).")
            return False

        if not all(isinstance(dim, int) for dim in resolution_tuple):
            logging.error(f"Размеры разрешения '{resolution_name}' должны быть целыми числами.")
            return False

        if not all(dim > 0 for dim in resolution_tuple):  # Проверка на положительные размеры
             logging.error(f"Размеры разрешения '{resolution_name}' должны быть положительными целыми числами.")
             return False

    return True

async def can_admin_interact(admin_id, target_id):
    admin_level = await get_admin_level(admin_id)
    target_level = await get_admin_level(target_id)

    # Проверяем, не пытается ли администратор взаимодействовать с самим собой
    if admin_id == target_id:
        return False

    # Проверяем, не пытается ли администратор взаимодействовать с администратором выше по рангу
    if admin_level < target_level:
        return False

    return True
    

async def update_user_info(user_id, user: types.User):
    username = user.username or ''
    first_name = user.first_name or ''
    last_name = user.last_name or ''

    try:
        # Проверяем, существует ли уже пользователь в базе данных
        existing_user = await execute_query_single('bot_data.db', "SELECT user_id FROM users WHERE user_id = ?", (user_id,))

        if not existing_user:  # Если пользователя нет в базе
            if ENGEENER_LOGS:
                logging.info(f"Добавление нового пользователя: {user_id}, username: {username}")
            success_users = await execute_update(
                'bot_data.db', 
                "INSERT INTO users (user_id, username, first_name, last_name) VALUES (?, ?, ?, ?)", 
                (user_id, username.lower() if username else '-', first_name, last_name)
            )
            if ENGEENER_LOGS:
                logging.info(f"Добавление в таблицу users {'успешно' if success_users else 'неуспешно'} для пользователя: {user_id}")

            success_profile = await execute_update(
                'bot_data.db', 
                "INSERT INTO user_profile (user_id, username) VALUES (?, ?)", 
                (user_id, username.lower() if username else '-')
            )
            if ENGEENER_LOGS:
                logging.info(f"Добавление в таблицу user_profile {'успешно' if success_profile else 'неуспешно'} для пользователя: {user_id}")
        else:  # Если пользователь уже существует, обновляем его данные
            if ENGEENER_LOGS:
                logging.info(f"Обновление существующего пользователя: {user_id}, username: {username}")
            success_users = await execute_update(
                'bot_data.db', 
                "UPDATE users SET username = ?, first_name = ?, last_name = ? WHERE user_id = ?", 
                (username.lower() if username else '-', first_name, last_name, user_id)
            )
            if ENGEENER_LOGS:
                logging.info(f"Обновление в таблице users {'успешно' if success_users else 'неуспешно'} для пользователя: {user_id}")

            success_profile = await execute_update(
                'bot_data.db', 
                "UPDATE user_profile SET username = ? WHERE user_id = ?", 
                (username.lower() if username else '-', user_id)
            )
            if ENGEENER_LOGS:
                logging.info(f"Обновление в таблице user_profile {'успешно' if success_profile else 'неуспешно'} для пользователя: {user_id}")
    except Exception as e:
        logging.exception(f"Ошибка при обновлении пользовательской информации для ID {user_id}: {e}")
    
async def check_channel_subscription(user_id, pyrogram_client):
    """Проверяет подписку на канал с попытками и экспоненциальным backoff."""
    max_retries = 5
    for attempt in range(1, max_retries + 1):
        try:
            chat_member = await pyrogram_client.get_chat_member(CHANNEL, user_id)
            return chat_member.status != ChatMemberStatus.LEFT
        except errors.UserNotParticipant:
            return False  # Пользователь точно не подписан
        except errors.RPCError as e:
            logging.warning(f"Ошибка Pyrogram RPC (попытка {attempt}/{max_retries}): {e}. Повторяем...")
            await asyncio.sleep(attempt * 2)
        except Exception as e:
            logging.exception(f"Непредвиденная ошибка при проверке подписки (попытка {attempt}/{max_retries}): {e}")
            await asyncio.sleep(attempt * 2)
    if ENGEENER_LOGS:
        logging.error(f"Не удалось проверить подписку для пользователя {user_id} после нескольких попыток.")
    return False
    
async def periodic_subscription_check():
    while True:
        users = await execute_query('bot_data.db', "SELECT user_id FROM users")
        for user in users:
            user_id = user[0]
            await check_channel_subscription(user_id, pyrogram_client)  # Добавил pyrogram_client
        await asyncio.sleep(CHECK_INTERVAL)

async def is_admin(user_id, db_name='bot_data.db'):
    try:
        result = await execute_query_single(db_name, "SELECT level FROM admins WHERE user_id = ?", (user_id,))
        return result and result[0] >= 1
    except Exception as e:
        logging.exception(f"Ошибка в is_admin: {e}")
        return False

async def get_admin_level(user_id, db_name='bot_data.db'):
    try:
        result = await execute_query_single(db_name, "SELECT level FROM admins WHERE user_id = ?", (user_id,))
        return result[0] if result else 0
    except Exception as e:
        logging.exception(f"Ошибка в get_admin_level: {e}")
        return 0

async def is_banned(user_id, db_name='bot_data.db'):
    try:
        async with aiosqlite.connect(db_name) as db:
            async with db.cursor() as cursor:
                await cursor.execute("SELECT ban_until FROM banned_users WHERE user_id = ?", (user_id,))
                result = await cursor.fetchone()
                if result:
                    ban_until = result[0]
                    if ban_until == -1:
                        return True
                    if time.time() < ban_until:
                        return True
                    await cursor.execute("DELETE FROM banned_users WHERE user_id = ?", (user_id,))
                    await db.commit()
                return False
    except Exception as e:
        logging.exception(f"Ошибка в is_banned: {e}")
        return False

def parse_duration(duration_text):
    time_units = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400, 'w': 604800, 'y': 31536000}
    match = re.match(r'^(\d+)([smhdwy]?)$', duration_text)
    if match:
        value, unit = match.groups()
        try:
            value = int(value)
            unit = unit or 's'
            return value * time_units[unit] if unit in time_units else None
        except ValueError:
            logging.error(f"Некорректное числовое значение в duration: {duration_text}")
            return None
    elif duration_text.lower() == 'forever':
        return -1
    else:
        if ENGEENER_LOGS:
            logging.error(f"Неверный формат duration: {duration_text}")
        return None

def format_time_left(ban_until):
    if ban_until == -1:
        return "навсегда"
    time_left = ban_until - time.time()
    if time_left <= 0:
        return "бан уже закончился"
    seconds = int(time_left)
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    result = []
    if days: result.append(f"{days} дн.")
    if hours: result.append(f"{hours} ч.")
    if minutes: result.append(f"{minutes} мин.")
    if seconds and not (days or hours or minutes): result.append(f"{seconds} сек.")
    return ", ".join(result) or "менее 1 секунды"

def hbold(text):
    return f"<b>{text}</b>"

# Функция для экспорта истории чата в JSON

async def export_chat_history(user_id, pyrogram_client: Client):
    """Экспортирует историю чата в JSON файл с именем пользователя и информацией."""
    try:
        context = await get_context(user_id)
        if not context:
            if ENGEENER_LOGS:
                logging.warning(f"Контекст для пользователя {user_id} пуст.")
            return None

        user_info = await get_user(user_id)
        if user_info is None:
            if ENGEENER_LOGS:
                logging.warning(f"Пользователь с ID {user_id} не найден.")
            return None

        username = user_info.get('username', 'Неизвестный пользователь')

        json_data = {"messages": context, "username": username}

        try:
            json_str = json.dumps(json_data, ensure_ascii=False, indent=4)
        except json.JSONEncodeError as e:
            logging.exception(f"Ошибка кодирования JSON: {e}")
            return None

        temp_dir = "./Temp"
        os.makedirs(temp_dir, exist_ok=True)
        temp_file_path = os.path.join(temp_dir, f"history_{user_id}.json")
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(json_str.encode('utf-8'))
        return temp_file_path

    except (errors.RPCError, Exception) as e:
        logging.exception(f"Ошибка при экспорте истории чата: {e}")
        return None

# Функция для импорта истории чата из JSON
async def import_chat_history(user_id, json_data):
    try:
        data = json.loads(json_data)
        #print(f"Данные, полученные в import_chat_history: {data}")
        if not isinstance(data, dict) or "messages" not in data:  # Проверка, является ли это словарем с ключом 'messages'
            return False  # Неверный формат JSON

        messages = data["messages"]  # Доступ к массиву сообщений
        if not isinstance(messages, list):
            return False  # Неверный формат JSON

        for item in messages:  # Итерация по массиву сообщений
            if not isinstance(item, dict) or "role" not in item or "content" not in item:
                return False

        await clear_context(user_id)
        for item in messages:
            await save_message(user_id, item["role"], item["content"])
        return True
    except json.JSONDecodeError:
        logging.exception("Неверный формат JSON")
        return False
    except Exception as e:
        logging.exception(f"Ошибка импорта истории чата: {e}")
        return False

async def get_user(user_id):
    result = await execute_query_single('bot_data.db', "SELECT username, first_name, last_name FROM users WHERE user_id = ?", (user_id,))
    if result:
        username = result[0]
        first_name = result[1]
        last_name = result[2]
        return {'username': username, 'first_name': first_name, 'last_name': last_name}  # Возвращаем словарь с именами пользователя
    else:
        return None
        
def create_models_keyboard():
    # Используем множество для хранения уникальных моделей
    unique_models = set()

    # Собираем все модели из API_PROVIDERS
    for provider in API_PROVIDERS.values():
        unique_models.update(provider['models'])  # Добавляем модели в множество

    # Создаем кнопки для каждой уникальной модели
    buttons = [InlineKeyboardButton(text=model, callback_data=f"set_model:{model}") for model in unique_models]

    # Добавляем кнопки в клавиатуру (по 2 в ряд)
    rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]

    # Создаем InlineKeyboardMarkup с правильной структурой
    models_keyboard = InlineKeyboardMarkup(inline_keyboard=rows)

    # Добавляем кнопку "Назад"
    models_keyboard.inline_keyboard.append([InlineKeyboardButton(text=back_txt, callback_data="main_menu")])

    return models_keyboard

def create_img_models_keyboard():
    # Используем множество для хранения уникальных моделей
    unique_models = set()

    # Собираем все модели из API_PROVIDERS
    for provider in API_PROVIDERS_IMAGE.values():
        unique_models.update(provider['img_models'])  # Добавляем модели в множество

    # Создаем кнопки для каждой уникальной модели
    buttons = [InlineKeyboardButton(text=model, callback_data=f"set_model:{model}") for model in unique_models]

    # Добавляем кнопки в клавиатуру (по 2 в ряд)
    rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]

    # Создаем InlineKeyboardMarkup с правильной структурой
    models_keyboard = InlineKeyboardMarkup(inline_keyboard=rows)

    # Добавляем кнопку "Назад"
    models_keyboard.inline_keyboard.append([InlineKeyboardButton(text=back_txt, callback_data="main_menu")])

    return models_keyboard

async def get_user_id(user_input, bot: Client):
    if ENGEENER_LOGS:
        logging.debug(f"get_user_id called with user_input: {user_input}")
    try:
        if ENGEENER_LOGS:
            logging.debug(f"Before lower: user_input: {user_input}")
        user_input_lower = user_input.lower()
        if ENGEENER_LOGS:
            logging.debug(f"After lower: user_input_lower: {user_input_lower}")

        if user_input_lower.isdigit():
            if ENGEENER_LOGS:
                logging.debug(f"Is digit: {user_input_lower}")
            user_id = int(user_input_lower)
            if ENGEENER_LOGS:
                logging.debug(f"User ID received directly: {user_id}")
            return user_id
        elif user_input_lower.startswith('@'):
            if ENGEENER_LOGS:
                logging.debug(f"Starts with @: {user_input_lower}")
            username = user_input_lower[1:]
            if ENGEENER_LOGS:
                logging.debug(f"Username after remove @: {username}")
            try:
               if ENGEENER_LOGS:
                    logging.debug("Before DB query")
               result = await execute_query_single('bot_data.db', "SELECT user_id FROM users WHERE LOWER(username) = ?", (username,))
               if ENGEENER_LOGS:
                    logging.debug(f"After DB query, result: {result}")
               if result:
                  user_id = result[0]
                  if ENGEENER_LOGS:
                    logging.debug(f"User ID found in database: {user_id}")
                  return user_id
               else:
                  if ENGEENER_LOGS:
                    logging.debug(f"User not found in database, querying Pyrogram for username: {username}")
                  try:
                      if ENGEENER_LOGS:
                        logging.debug("Before Pyrogram query")
                      user = await bot.get_users(username)
                      if ENGEENER_LOGS:
                        logging.debug(f"After Pyrogram query, user: {user}")
                      if user:
                         user_id = user.id
                         if ENGEENER_LOGS:
                            logging.debug(f"User ID received from Pyrogram: {user_id}")
                         await update_user_info(user_id, user)
                         return user_id
                      else:
                         if ENGEENER_LOGS:
                            logging.warning(f"User '{username}' not found using Pyrogram.")
                         return None
                  except errors.UsernameNotOccupied:
                        logging.warning(f"Username '{username}' is not occupied.")
                        return None
                  except errors.UsernameInvalid:
                        logging.warning(f"Invalid username '{username}'.")
                        return None
                  except errors.RPCError as e:
                        logging.error(f"Pyrogram RPC error: {e}")
                        return None
                  except Exception as e:
                       logging.exception(f"An unexpected error occurred during Pyrogram query: {e}")
                       return None
            except Exception as e:
                logging.exception(f"Database query error: {e}")
                return None
        else:
           if ENGEENER_LOGS:
            logging.debug(f"Invalid user input format: {user_input}")
           return None

    except Exception as e:
      logging.exception(f"Error in get_user_id: {e}")
      return None

async def set_user_model(user_id, model):
    await execute_update('bot_data.db', "INSERT OR IGNORE INTO user_profile (user_id, model) VALUES (?, ?)", (user_id, model))
    await execute_update('bot_data.db', "UPDATE user_profile SET model = ? WHERE user_id = ?", (model, user_id))

async def get_user_model(user_id):
    result = await execute_query_single('bot_data.db', "SELECT model FROM user_profile WHERE user_id = ?", (user_id,))
    return result[0] if result else "gpt-4o-mini"

async def set_image_model(user_id, img_model):
    await execute_update('bot_data.db', "INSERT OR IGNORE INTO user_profile (user_id, img_model) VALUES (?, ?)", (user_id, img_model))
    await execute_update('bot_data.db', "UPDATE user_profile SET img_model = ? WHERE user_id = ?", (img_model, user_id))

async def get_image_model(user_id):
    result = await execute_query_single('bot_data.db', "SELECT img_model FROM user_profile WHERE user_id = ?", (user_id,))
    return result[0] if result else "flux"

async def get_context(user_id):
    rows = await execute_query('_history.db', "SELECT role, message FROM messages WHERE user_id = ? ORDER BY rowid ASC", (user_id,))
    return [{"role": row[0], "content": row[1]} for row in rows]

async def save_message(user_id, role, message):
    await execute_update('_history.db', "INSERT INTO messages (user_id, role, message) VALUES (?, ?, ?)", (user_id, role, message))
    await execute_update('_history.db', """DELETE FROM messages WHERE user_id = ? AND rowid NOT IN (SELECT rowid FROM messages WHERE user_id = ? ORDER BY rowid DESC LIMIT 10000)""", (user_id, user_id))

async def clear_context(user_id):
    await execute_update('_history.db', "DELETE FROM messages WHERE user_id = ?", (user_id,))
    

async def start_typing(bot: Bot, user_id: int):
    """Запускает индикатор 'печатает...' в Telegram."""
    try:
        await bot.send_chat_action(chat_id=user_id, action="typing")
    except TelegramAPIError as e:
        logging.warning(f"Ошибка при отправке индикатора 'печатает...': {e}")

async def stop_typing(bot: Bot, user_id: int):
    """Останавливает индикатор 'печатает...'."""
    try:
        await bot.send_chat_action(chat_id=user_id, action="cancel")
    except TelegramAPIError as e:
        logging.warning(f"Ошибка при остановке индикатора 'печатает...': {e}")
    
async def add_coins(user_id, coins):
    """Функция для добавления монет пользователю в базу данных."""
    current_balance = await execute_query_single('bot_data.db', 
            "SELECT balance FROM user_profile WHERE user_id = ?", (user_id,)
        )
    if current_balance is not None:
        current_balance = current_balance[0]
        new_balance = current_balance + coins
        update_successful = await execute_update('bot_data.db',
                "UPDATE user_profile SET balance = ? WHERE user_id = ?",
                (new_balance, user_id)
            )
        if update_successful:
            if ENGEENER_LOGS:
                logging.info(f"Пользователю {user_id} начислено {coins} монет. Новый баланс: {new_balance}")
        else:
            if ENGEENER_LOGS:
                logging.error(f"Не удалось начислить монеты пользователю {user_id}.")
    else:
        if ENGEENER_LOGS:
            logging.error(f"Пользователь с ID {user_id} отсутствует в базе данных.")
    
async def send_message_with_retry(bot, chat_id, text, reply_markup=None, parse_mode="Markdown"):
    max_retries = 5
    for attempt in range(1, max_retries + 1):
        try:
            if reply_markup is not None:
                await bot.send_message(chat_id, text, reply_markup=reply_markup, parse_mode=parse_mode)
            else:
                await bot.send_message(chat_id, text, parse_mode=parse_mode)
            return True
        except TelegramAPIError as e:
            logging.warning(f"Ошибка Telegram API (попытка {attempt}/{max_retries}): {e}. Повторяем...")
            await asyncio.sleep(attempt * 2)  # Экспоненциальный backoff
    if ENGEENER_LOGS:
        logging.error(f"Не удалось отправить сообщение после нескольких попыток: {text}")
    return False
    
TELEGRAPH_THRESHOLD = 4000

async def add_response_to_server(session, title, text):
    """Adds a response to the server using aiohttp."""
    url = f"{URL}:{WEB_PORT}/add_response"
    try:
        async with session.post(url, json={"title": title, "text": text}) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("response_id")
            else:
                if ENGEENER_LOGS:
                    logging.error(f"Ошибка добавления ответа на сервер: {response.status} - {await response.text()}")
                return None
    except aiohttp.ClientError as e:
        logging.error(f"Ошибка подключения к серверу: {e}")
        return None

async def convert_markdown_to_html(text: str) -> str:
    """Конвертирует Markdown в HTML в отдельном потоке."""
    loop = asyncio.get_running_loop()
    extras = ["fenced-code-blocks", "tables", "header-ids", "code-friendly"]

    def markdown_wrapper(text, extras):
        return markdown2.markdown(text, extras=extras)

    return await loop.run_in_executor(None, markdown_wrapper, text, extras)

async def clean_html(html: str) -> str:
    """Очищает HTML в отдельном потоке."""
    loop = asyncio.get_running_loop()


    def bleach_wrapper(html, tags, attributes, strip):
      return bleach.clean(html, tags=tags, attributes=attributes, strip=strip)

    return await loop.run_in_executor(None, bleach_wrapper, html, ALLOWED_TAGS, ALLOWED_ATTRIBUTES, True)

async def parse_html(html: str) -> BeautifulSoup:
    """Парсит HTML в отдельном потоке."""
    loop = asyncio.get_running_loop()

    def bs4_wrapper(html, parser):
        return BeautifulSoup(html, parser)

    return await loop.run_in_executor(None, bs4_wrapper, html, "html.parser")

async def periodic_typing(bot: Bot, user_id: int, stop_event: asyncio.Event):
    """Периодически отправляет индикатор 'печатает...', пока не будет установлен stop_event."""
    try:
        while not stop_event.is_set():
            await bot.send_chat_action(chat_id=user_id, action="typing")
            await asyncio.sleep(1)  # Отправляем каждую секунду (можно настроить)
    except TelegramAPIError as e:
        logging.warning(f"Ошибка при отправке индикатора 'печатает...': {e}")

async def generate_response(user_id: int, user_message: str, bot: Bot) -> None:
    """Генерирует ответ, используя блокировку и периодический индикатор 'печатает...'."""
    if user_id not in user_locks:
        user_locks[user_id] = asyncio.Lock()

    try:
        async with user_locks[user_id]:
            stop_typing_event = asyncio.Event()  # Создаем событие для остановки periodic_typing
            typing_task = asyncio.create_task(periodic_typing(bot, user_id, stop_typing_event))  # Запускаем задачу

            try:
                response_message = None
                await asyncio.wait_for(process_generation(user_id, user_message, bot, stop_typing_event), TIMEOUT_SECONDS)
                if ENGEENER_LOGS:
                    logging.warning(f"Пользователь {user_id} превысил таймаут ожидания обработки запроса.")
            except TelegramAPIError as e:
                logging.exception(f"Ошибка Telegram API для пользователя {user_id}: {e}")
                await send_message_with_retry(bot, user_id, f"Ошибка Telegram API: {e}", parse_mode=ParseMode.HTML)
            except Exception as e:
                logging.exception(f"Непредвиденная ошибка для пользователя {user_id}: {e}")
                await send_message_with_retry(bot, user_id, "Произошла неизвестная ошибка. Попробуйте позже.", parse_mode=ParseMode.HTML)
            finally:
                stop_typing_event.set()  # Даем сигнал задаче periodic_typing остановиться
                await asyncio.sleep(0.5) # Даем время задаче на остановку

    finally:
        if 'typing_task' in locals() and not typing_task.done():
            stop_typing_event.set()
            await typing_task  # Ensure the typing task is awaited to avoid ResourceWarning

    return None

async def process_generation(user_id: int, user_message: str, bot: Bot, stop_typing_event: asyncio.Event):
    """Выполняет основную логику генерации ответа."""
    try:
        model_name = await get_user_model(user_id)
        context = await get_context(user_id)
        context.insert(0, {"role": "system", "content": system_prompt})
        context.append({"role": "user", "content": user_message})

        await save_message(user_id, "user", user_message)

        random_coins = random.randint(0, 25)
        await add_coins(user_id, random_coins)

        # Получаем текущее количество запросов
        current_requests_count = await execute_query_single('bot_data.db',
            "SELECT requests_count FROM user_profile WHERE user_id = ?", (user_id,)
        )
        if current_requests_count is not None:
            current_requests_count = current_requests_count[0]
            if ENGEENER_LOGS:
                logging.info(f"Текущее количество запросов для пользователя {user_id} перед обновлением: {current_requests_count}")

        # Увеличиваем счетчик запросов
        new_requests_count = current_requests_count + 1
        update_successful = await execute_update('bot_data.db',
            "UPDATE user_profile SET requests_count = ? WHERE user_id = ?",
            (new_requests_count, user_id)
        )

        if update_successful:
            if ENGEENER_LOGS:
                logging.info(f"Количество запросов обновлено для пользователя {user_id}: {new_requests_count}")
        else:
            if ENGEENER_LOGS:
                logging.error(f"Не удалось обновить количество запросов для пользователя {user_id}.")
                logging.error(f"Пользователь с ID {user_id} отсутствует в базе данных.")

        response_message = await try_api_providers(model_name, context)
        short_response = response_message
        if response_message:
            await save_message(user_id, "assistant", response_message)
            response_message = response_message.strip()
            if ENGEENER_LOGS:
                logging.info(f"Ответ модели (перед обработкой): {response_message}")

            try:
                # Асинхронно конвертируем Markdown в HTML
                html_content = await convert_markdown_to_html(response_message)

                # Асинхронно очищаем HTML
                cleaned_html = await clean_html(html_content)

                # Асинхронно парсим HTML
                soup = await parse_html(cleaned_html)

                if soup.find(lambda tag: tag.name is None):
                    cleaned_html = "Ошибка в ответе модели. Сгенерирован неверный HTML."

                if len(cleaned_html) <= TELEGRAPH_THRESHOLD:
                    await send_message_with_retry(bot, user_id, short_response, parse_mode=ParseMode.MARKDOWN)
                    if ENGEENER_LOGS:
                        logging.info(f"Отправлен короткий ответ пользователю {user_id}: {response_message}")
                else:
                    async with aiohttp.ClientSession() as session:
                        response_id = await add_response_to_server(session, "Ответ от бота", cleaned_html)
                    if response_id:
                        response_url = f"{URL}:{WEB_PORT}/response/{response_id}"
                        full_url = f"{URL}:{WEB_PORT}/response/{response_id}"
                        mobile_url = f"{URL}:{WEB_PORT}/response/{response_id}?mobile=true"

                        # Создание разметки для кнопок
                        response_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="Мобильная версия📱", url=mobile_url),
                             InlineKeyboardButton(text="Полная версия🖥️", url=full_url)]
                        ])

                        # Отправка сообщения с кнопками
                        await bot.send_message(
                            chat_id=user_id,
                            text="Ответ доступен по кнопке снизу",
                            parse_mode=ParseMode.HTML,
                            reply_markup=response_keyboard
                        )
                        if ENGEENER_LOGS:
                            logging.info(f"Отправлен длинный ответ пользователю {user_id} на сервер. Ссылка: {response_url}")
                    else:
                        await send_message_with_retry(bot, user_id, "Ошибка при отправке ответа на сервер. Попробуйте позже.", parse_mode=ParseMode.HTML)
                        if ENGEENER_LOGS:
                            logging.error(f"Ошибка при отправке ответа на сервер для пользователя {user_id}.")

            except Exception as e:
                logging.exception(f"Ошибка обработки ответа модели: {e}")
                await send_message_with_retry(bot, user_id, f"Ошибка обработки ответа модели: {e}", parse_mode=ParseMode.HTML)
        else:
            await send_message_with_retry(bot, user_id, "Ошибка: Не удалось получить ответ от модели. Попробуйте позже.", parse_mode=ParseMode.HTML)
            if ENGEENER_LOGS:
                logging.error(f"Ошибка получения ответа от модели для пользователя {user_id}.")

    except Exception as e:
        logging.exception(f"Ошибка при генерации ответа: {e}")
        await send_message_with_retry(bot, user_id, "Произошла ошибка при генерации ответа.", parse_mode=ParseMode.HTML)

    return None


async def try_image_api_providers(img_model, img_query, resolution_key):
    """Tries to use different image API providers until a successful response is received."""
    provider_states = {name: 0 for name in API_PROVIDERS_IMAGE}
    provider_queue = list(API_PROVIDERS_IMAGE.keys())

    if resolution_key not in RESOLUTIONS:
        if ENGEENER_LOGS:
            logging.error(f"Unknown resolution key: {resolution_key}. It must be one of: {list(RESOLUTIONS.keys())}")
        return None

    resolution = RESOLUTIONS[resolution_key]

    while provider_queue:
        provider_name = provider_queue[0]
        provider_data = API_PROVIDERS_IMAGE[provider_name]

        if ENGEENER_LOGS:
            logging.info(f"Checking provider: {provider_name} with model: {img_model}")

        if img_model in provider_data.get("img_models", []):
            try:
                image_url = await call_image_api(
                    provider_data["base_url"], 
                    provider_data["api_key"], 
                    img_model, 
                    img_query, 
                    resolution
                )
                provider_states[provider_name] = 0
                if ENGEENER_LOGS:
                    logging.info(f"Image obtained successfully from provider: {provider_name}")
                return image_url
            except (OpenAIError, requests.exceptions.RequestException) as e:
                logging.warning(f"Error with API {provider_name} for image: {e}. Trying another provider...")
                provider_states[provider_name] += 1

                if provider_states[provider_name] >= 2:
                    provider_queue.append(provider_queue.pop(0))
                    logging.info(f"Provider {provider_name} moved to the end of the list.")
        else:
            if ENGEENER_LOGS:
                logging.info(f"Model {img_model} not supported by provider {provider_name}.")

        provider_queue.pop(0)

    if ENGEENER_LOGS:
        logging.error("All providers failed to return an image.")
    return None

active_providers = list(API_PROVIDERS.keys())  # Создаем начальный список провайдеров

async def call_api_async(session: aiohttp.ClientSession, base_url: str, api_key: str, model_name: str, context: list, proxy: Optional[str] = None):
    """Вызывает API асинхронно с поддержкой прокси."""
    try:
        if proxy:
            if not await check_proxy(proxy):
                logging.warning(f"Прокси {proxy} не работает, пропуск запроса.")
                return None # Пропускаем запрос, если прокси не работает

        async with session.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": model_name, "messages": context, "temperature": 0.5},
            timeout=120,  # Ограничение по времени на запрос
            proxy=proxy  # Добавляем прокси
        ) as response:
            response.raise_for_status()  # Проверка на HTTP ошибки
            data = await response.json()
            return data["choices"][0]["message"]["content"].strip()
    except (aiohttp.ClientError, OpenAIError, requests.exceptions.RequestException) as e:
        logging.warning(f"Ошибка при вызове API: {e}")
        return None  # Или другое значение по умолчанию в случае ошибки

async def try_api_providers(model_name: str, context: list) -> str | None:
    """Пытается использовать разные API-провайдеры параллельно."""
    global active_providers

    if ENGEENER_LOGS:
        logging.info(f"Активные провайдеры: {active_providers}")

    async with aiohttp.ClientSession() as session:  # Используем aiohttp для асинхронных запросов
        tasks = []
        for provider_name in list(active_providers):
            provider_data = API_PROVIDERS.get(provider_name)
            if not provider_data:
                continue
            if model_name in provider_data["models"]:
                proxy = provider_data.get("proxy")  # Получаем прокси для данного провайдера
                task = asyncio.create_task(
                    call_api_async(session, provider_data["base_url"], provider_data["api_key"], model_name, context, proxy=proxy)
                )
                tasks.append(task)

        if not tasks:
            logging.warning("Нет подходящих API-провайдеров для данной модели.")
            return None

        # Используем asyncio.as_completed, чтобы получить результаты по мере готовности.
        for future in asyncio.as_completed(tasks):
            try:
                result = await future
                if result:
                    # Отменяем все остальные задачи.
                    for task in tasks:
                        task.cancel()
                    return result
            except asyncio.CancelledError:
                pass  # Задача была отменена
            except Exception as e:
                logging.exception(f"Ошибка при получении результата от задачи: {e}")

    return None  # Если все провайдеры вернули ошибку или были отменены
        
async def generate_image(user_id, img_query, resolution_key, bot):
    """Asynchronous function to handle image generation using the user's selected model and resolution."""
    await start_typing(bot, user_id)
    try:
        async with image_generation_semaphore:
            img_model = await get_image_model(user_id)
            resolution = RESOLUTIONS.get(resolution_key, (512, 512))
            preferred_provider = None
            for provider_name, provider_data in API_PROVIDERS_IMAGE.items():
                if 'img_models' in provider_data and img_model in provider_data["img_models"]:
                    if preferred_provider is None or provider_name == preferred_provider:
                        try:
                            return await call_image_api(provider_data["base_url"], provider_data["api_key"], img_model, img_query, resolution)
                        except (OpenAIError, requests.exceptions.RequestException) as e:
                            logging.warning(f"Ошибка с API {provider_name} для изображения: {e}. Пробуем другого провайдера...")
                    else:
                        if ENGEENER_LOGS:
                            logging.info(f"Модель изображения {img_model} поддерживается {provider_name}, но предпочтительнее {preferred_provider}. Пропускаем.")
            return None

    except Exception as e:
        logging.exception(f"Ошибка генерации изображения: {e}")
        await send_message_with_retry(bot, user_id, f"Ошибка генерации изображения: {e}", parse_mode=ParseMode.HTML)
    finally:
        await stop_typing(bot, user_id)

async def call_image_api(base_url, api_key, img_model, img_query, resolution):
    """Function to handle image API calls."""
    async with aiohttp.ClientSession() as session:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # Форматируем размер как строку "ШиринаxВысота"
        size_str = f"{resolution[0]}x{resolution[1]}"
        
        data = {
            'model': img_model,
            'prompt': img_query,
            'size': size_str  # Используем конкатенированную строку здесь
        }
        
        async with session.post(base_url, headers=headers, json=data) as response:
            if response.status == 200:
                result = await response.json()
                return result['data'][0]['url']
            else:
                text = await response.text()
                raise OpenAIError(f"Failed to get image: {response.status}, {text}")
       
async def ban_user(message: types.Message):
    if not await is_admin(message.from_user.id):
        return await message.reply("У вас нет прав.")

    args = message.text.split(maxsplit=3)
    if len(args) < 3:
        return await message.reply("Не указана причина бана или время бана. Используйте: /ban <@username|user_id> <duration (m, h, d, forever)> <reason>")

    try:
        user_id = await get_user_id(args[1], bot)
        user_name = args[1]

        if user_id is None:
            return await message.reply(f"Пользователь {user_name} не найден.")

        # Проверка прав взаимодействия
        if not await can_admin_interact(message.from_user.id, user_id):
            return await message.reply("Вы не можете забанить этого администратора.")

        duration_text = args[2]
        ban_reason = " ".join(args[3:])
        duration = parse_duration(duration_text)

        if duration is None or duration == 0:
            return await message.reply("Неверный формат времени бана.")

        now = datetime.now()
        ban_until = int((now + timedelta(seconds=duration) if duration != -1 else datetime.max).timestamp())

        async with database_lock:
            try:
                await execute_update('bot_data.db', "INSERT OR IGNORE INTO banned_users (user_id, ban_until, ban_reason, banned_by) VALUES (?, ?, ?, ?)", (user_id, ban_until, ban_reason, message.from_user.id))
                await execute_update('bot_data.db', "INSERT INTO ban_history (user_id, banned_by, ban_until, ban_reason, timestamp) VALUES (?, ?, ?, ?, ?)", (user_id, message.from_user.id, ban_until, ban_reason, int(time.time())))
            except Exception as e:
                logging.exception(f"Произошла ошибка в ban_user (база данных): {e}")
                return await message.reply(f"Произошла ошибка при работе с базой данных: {e}")

        try:
            await bot.send_message(user_id, f"Вас забанил @{message.from_user.username} на {format_time_left(ban_until)} по причине:\n{ban_reason}")
        except TelegramAPIError as e:
            logging.warning(f"Не удалось отправить сообщение пользователю {user_name}: {e}")
            await message.reply(f"Пользователь с ID {user_name} забанен, но сообщение не отправлено.", parse_mode="HTML")

        try:
            if ADMIN_LOGGING == True:
                if IS_SUPERGROUP == True:
                    await bot.send_message(BOT_LOGS_CHANNEL, f"Пользователь с ID {user_name} забанен на {format_time_left(ban_until)} администратором @{message.from_user.username} по причине:\n{ban_reason}", message_thread_id=BAN_THREAD)
                else:
                    await bot.send_message(BOT_LOGS_CHANNEL, f"Пользователь с ID {user_name} забанен на {format_time_left(ban_until)} администратором @{message.from_user.username} по причине:\n{ban_reason}")
            else:
                return
        except TelegramAPIError as e:
            logging.exception(f"Произошла ошибка при отправлении лога: {e}")

        await message.reply(f"Пользователь с ID {user_name} забанен на {format_time_left(ban_until)} по причине:\n{ban_reason}")

    except Exception as e:
        logging.exception(f"Произошла ошибка в ban_user (другая ошибка): {e}")
        await message.reply(f"Произошла ошибка: {e}")
                
async def unban_user(message: types.Message):
    if not await is_admin(message.from_user.id):
        return await message.reply("У вас нет прав.")

    args = message.text.split()
    if len(args) < 2:
        return await message.reply("Не указан пользователь для разбана. Используйте: /unban <@username|user_id>")

    try:
        user_id = await get_user_id(args[1], bot)
        user_name = args[1]

        if user_id is None:
            return await message.reply(f"Пользователь '{user_name}' не найден.")

        # Проверка прав взаимодействия
        if not await can_admin_interact(message.from_user.id, user_id):
            return await message.reply("Вы не можете разбанить этого администратора.")

        async with database_lock:
            try:
                success = await execute_update('bot_data.db', "DELETE FROM banned_users WHERE user_id = ?", (user_id,))
                if success:
                    await message.reply(f"Пользователь с ID '{user_name}' разбанен.")
                    await bot.send_message(user_id, f"Вы были разбанены администратором @{message.from_user.username}") 
                else:
                    await message.reply(f"Ошибка удаления бана для пользователя с ID {user_name}.")
            except Exception as e:
                logging.exception(f"Произошла ошибка в unban_user: {e}")
                await message.reply(f"Произошла ошибка: {e}")

        try:
            if ADMIN_LOGGING == True:
                if IS_SUPERGROUP == True:
                    await bot.send_message(BOT_LOGS_CHANNEL, f"Пользователь с ID {user_name} был разбанен администратором @{message.from_user.username}", message_thread_id=UNBAN_THREAD)
                else:
                    await bot.send_message(BOT_LOGS_CHANNEL, f"Пользователь с ID {user_name} был разбанен администратором @{message.from_user.username}")
            else:
                return
        except TelegramAPIError as e:
            logging.exception(f"Произошла ошибка при отправлении лога: {e}")
    except Exception as e:
        logging.exception(f"Ошибка при получении user_id в unban_user: {e}")
        await message.reply(f"Произошла ошибка: {e}")

async def clear_command(message: types.Message):
    args = message.text.split()
    try:
        if len(args) > 1:
            if not await is_admin(message.from_user.id) or not (await get_admin_level(message.from_user.id) >= 3):
                return await message.reply("У вас нет прав.")
            user_input = args[1]
            if not (user_input.isdigit() or re.match(r'^@\w+$', user_input)):
                return await message.reply("Неверный формат user_id или username.")
            user_id = await get_user_id(user_input, bot)
            if user_id is None:
                return await message.reply("Пользователь не найден.")
                
            # Проверка прав взаимодействия
            if not await can_admin_interact(message.from_user.id, user_id):
                return await message.reply("Вы не можете очистить контекст этого администратора.")
                
            admin_name = message.from_user.username
        else:
            user_id = message.from_user.id
            admin_name = None

        async with database_lock:
            try:
                success = await execute_update('_history.db', "DELETE FROM messages WHERE user_id = ?", (user_id,))
                if success:
                    await message.reply(f"{'Контекст пользователя ' + (f'{user_input} ' if admin_name else '') + 'очищен' + (f' админом @{admin_name}' if admin_name else '') + '.'}")
                    if admin_name:
                        try:
                            if ADMIN_LOGGING == True:
                                if IS_SUPERGROUP == True:
                                    await bot.send_message(BOT_LOGS_CHANNEL, f"@{admin_name} очистил контекст пользователя {user_input}", message_thread_id=UNBAN_THREAD)
                                else:
                                    await bot.send_message(BOT_LOGS_CHANNEL, f"@{admin_name} очистил контекст пользователя {user_input}")
                            else:
                                return
                        except TelegramAPIError as e:
                            logging.exception(f"Произошла ошибка при отправлении лога: {e}")
                        try:
                            await bot.send_message(user_id, f"Ваш контекст был очищен администратором @{admin_name}.")
                        except TelegramAPIError as e:
                            logging.error(f"Ошибка отправки сообщения пользователю {user_id}: {e}")
                else:
                    await message.reply("Ошибка очистки контекста.")
            except Exception as e:
                logging.exception(f"Произошла ошибка при очистке контекста: {e}")
                await message.reply("Произошла ошибка при очистке контекста. Попробуйте позже.")
    except Exception as e:
        logging.exception(f"Произошла общая ошибка в clear_command: {e}")
        await message.reply(f"Произошла ошибка: {e}")

async def get_broadcasts():
    async with aiosqlite.connect('bot_data.db') as db:
        async with db.execute("SELECT id, name, enabled FROM broadcasts ORDER BY creation_date DESC") as cursor:
            return await cursor.fetchall()

async def show_broadcast_menu(message: types.Message):
    broadcasts = await get_broadcasts()

    builder = InlineKeyboardBuilder()

    for broadcast in broadcasts:
        id, name, enabled = broadcast
        status = "✅" if enabled else "❌"
        builder.button(text=f"{name} {status}", callback_data=f"broadcast_{id}")

    builder.button(text="Создать новую", callback_data="create_broadcast")
    builder.adjust(1)  # Каждая кнопка на отдельной строке, adjust(1) делает то же самое

    await message.reply("Выберите рассылку для просмотра/редактирования или создайте новую.", reply_markup=builder.as_markup())

async def send_broadcast(broadcast_id):
    async with aiosqlite.connect('bot_data.db') as db:
        async with db.execute("SELECT text, media_id, media_type FROM broadcasts WHERE id = ?", (broadcast_id,)) as cursor:
            broadcast = await cursor.fetchone()
            if broadcast:
                text, media_id, media_type = broadcast
                users = await get_all_users()
                for user in users:
                    try:
                        username = user['username']
                        if username != "UNKNOWN_USER":
                            username = "@" + username

                        personalized_text = text.format(username=username, first_name=user['first_name'], last_name=user['last_name']) if text else ""

                        if media_id and media_type == "photo":
                            await bot.send_photo(user['user_id'], media_id, caption=personalized_text)
                        elif media_id and media_type == "video":
                            await bot.send_video(user['user_id'], media_id, caption=personalized_text)
                        elif media_id and media_type == "document":
                            await bot.send_document(user['user_id'], media_id, caption=personalized_text)
                        else:
                            await bot.send_message(user['user_id'], personalized_text)
                        await update_broadcast_stats(broadcast_id, success=True)
                    except Exception as e:
                        await update_broadcast_stats(broadcast_id, success=False, user_id=user['user_id'])
                        
async def update_broadcast_stats(broadcast_id, success, user_id=None):
    async with aiosqlite.connect('bot_data.db') as db:
        if success:
            await db.execute("UPDATE broadcasts SET successful = successful + 1, sent = sent + 1 WHERE id = ?", (broadcast_id,))
        else:
            await db.execute("UPDATE broadcasts SET failed = failed + 1, sent = sent + 1, failed_user_ids = failed_user_ids || ? || ',' WHERE id = ?", (user_id, broadcast_id,))
        await db.commit()

async def schedule_broadcast(state: FSMContext):
    data = await state.get_data()
    scheduled_time = data.get('scheduled_time')
    broadcast_text = data.get('broadcast_text')

    # Вычисляем время ожидания
    wait_time = (scheduled_time - datetime.now()).total_seconds()
    if wait_time > 0:
        await asyncio.sleep(wait_time)  # Ожидание до запланированного времени

    # Получаем всех пользователей для рассылки
    users = await get_all_users()
    for user in users:
        user_id = user['user_id']
        try:
            await bot.send_message(user_id, broadcast_text)
        except Exception as e:
            logging.error(f"Ошибка отправки сообщения пользователю {user_id}: {e}")

    await state.finish()  # Завершаем состояние после рассылки
         
async def get_all_users():
    async with aiosqlite.connect('bot_data.db') as db:
        async with db.execute("SELECT user_id, username, first_name, last_name FROM users") as cursor:
            users = await cursor.fetchall()
            return [{"user_id": user[0], "username": user[1], "first_name": user[2], "last_name": user[3]} for user in users]
            
async def process_queue(user_id: int, bot: Bot):
    """Асинхронно обрабатываем очередь сообщений для пользователя."""
    queue = user_queues[user_id]
    while True:
        message = await queue.get()  # Асинхронно получаем сообщение из очереди
        try:
            await process_message(message, user_id, bot)  # Асинхронно обрабатываем сообщение
        except Exception as e:
            logging.exception(f"Ошибка при обработке сообщения из очереди для пользователя {user_id}: {e}")
            await bot.send_message(user_id, "Произошла ошибка при обработке вашего запроса.")
        finally:
            queue.task_done()  # Подтверждаем завершение обработки задачи

async def process_message(message: types.Message, user_id: int, bot: Bot):
    """Асинхронно обрабатываем сообщение."""
    try:
        asyncio.create_task(update_last_seen(user_id)) # Запускаем обновление last_seen в фоне
        if message.text:
            asyncio.create_task(handle_message_text(message.text, user_id, bot)) # Запускаем обработку текста в фоне
    except Exception as e:
        logging.exception(f"Ошибка при обработке сообщения для пользователя {user_id}: {e}")
        await bot.send_message(user_id, "Произошла ошибка при обработке вашего запроса.")

async def update_last_seen(user_id: int):
    """Обновляем last_seen асинхронно."""
    await execute_update('bot_data.db', "UPDATE user_profile SET last_seen = ? WHERE user_id = ?", (int(time.time()), user_id))

async def handle_message_text(message_text: str, user_id: int, bot: Bot):
    """Обрабатываем текст сообщения асинхронно."""
    try:
        response_message = await generate_response(user_id, message_text, bot)
        if response_message:
            await bot.send_message(user_id, response_message)
    except Exception as e:
        logging.exception(f"Ошибка при генерации ответа: {e}")
        await bot.send_message(user_id, "Произошла ошибка при генерации ответа.")
        
async def download_and_decode_file(file_id, bot: Bot):
    try:
        file = await bot.get_file(file_id)
        bytes_io = await bot.download_file(file.file_path)
        return bytes_io.read().decode('utf-8', errors='ignore')
    except UnicodeDecodeError:
        logging.exception("Ошибка декодирования файла.")
        return None
    except TelegramAPIError as e:
        logging.exception(f"Ошибка Telegram API: {e}")
        return None
    except Exception as e:
        logging.exception(f"Произошла ошибка: {e}")
        return None

async def edit_broadcast_text(message: types.Message, broadcast_id: int, state: FSMContext):
    async with aiosqlite.connect('bot_data.db') as db:
        async with db.execute("SELECT name, text, media_id FROM broadcasts WHERE id = ?", (broadcast_id,)) as cursor:
            broadcast = await cursor.fetchone()
            if broadcast:
                name, text, media_id = broadcast
                # Отправляем текст рассылки для редактирования
                await message.reply(f"Редактирование рассылки: {name}\n\nТекущий текст:\n{text}\n\nВведите новый текст:")
                await BroadcastStates.waiting_for_text.set()  # Устанавливаем состояние ожидания текста
                await state.update_data(broadcast_id=broadcast_id)  # Сохраняем ID рассылки в состоянии
            else:
                await message.reply("Рассылка не найдена.")

async def check_channel_subscription_cached(user_id, pyrogram_client):
    """Проверяет подписку на канал с использованием кэша."""
    cache_key = user_id
    if cache_key in user_subscription_cache:
        cached_result, timestamp = user_subscription_cache[cache_key]
        if time.time() - timestamp < 60:  # Кэш действителен в течение 60 секунд
            return cached_result
        else:
            del user_subscription_cache[cache_key]  # Удаляем устаревший кэш

    is_subscribed = await check_channel_subscription(user_id, pyrogram_client)
    user_subscription_cache[cache_key] = (is_subscribed, time.time())
    return is_subscribed

async def check_proxy(proxy: str, url: str = "https://www.google.com", timeout: int = 5) -> bool:
    """Проверяет работоспособность прокси-сервера."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, proxy=proxy, timeout=timeout) as response:
                return response.status == 200
    except Exception as e:
        logging.warning(f"Прокси {proxy} не работает: {e}")
        return False

async def delete_message_after_delay(chat_id: int, message_id: int, delay: int):
    """Deletes a message after a specified delay."""
    await asyncio.sleep(delay)
    try:
        await bot.delete_message(chat_id, message_id)
    except Exception as e:
        logging.warning(f"Failed to delete message {message_id} in chat {chat_id}: {e}")

class OpenAIError(Exception):
    """Кастомное исключение для ошибок OpenAI API."""
    pass

class IsDocument(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        return message.content_type == types.ContentType.DOCUMENT
        
class BroadcastStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_text = State()
    waiting_for_media = State()
    waiting_for_time = State()
    confirmation = State()
async def main():
    global pyrogram_client, bot, dp, client, handle_all_messages_with_loop,handle_all_messages
    pyrogram_client = Client(BOT_USERNAME, api_id=API_ID, api_hash=API_HASH)
    try:
        if not await create_database('bot_data.db') or not await create_database('_history.db'):
            if ENGEENER_LOGS:
                logging.critical("Критическая ошибка при создании баз данных. Завершение работы.")
            return

        bot = Bot(token=BOT_TOKEN)
        dp = Dispatcher()
        dp.bot = bot
        main_menu_reply_keyboard = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text='✨Главное меню')]
        ], resize_keyboard=True)
    # Выбор модели (2 столбца + кнопка "Назад")
        img_models_keyboard = create_img_models_keyboard()
        
        await pyrogram_client.start()
        if not await check_authorization(pyrogram_client):
            if ENGEENER_LOGS:
                logging.critical("Авторизация клиента Pyrogram не удалась. Завершение работы.")
            return
            
        async def is_channel_banned(user_id):
            result = await execute_query_single('bot_data.db', "SELECT subscribed FROM channel_status WHERE user_id = ?", (user_id,))
            return result is None or result[0] == 0
            
        # Главное меню (изменённый layout)
        main_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🆔 Профиль", callback_data="profile"),
         InlineKeyboardButton(text="🤖 Выбор модели ChatGPT", callback_data="model_selection"),
         InlineKeyboardButton(text="🖼️ Выбор модели изображения", callback_data="img_model_selection")],
        [InlineKeyboardButton(text="🗑️ Очистить контекст", callback_data="clear_history"),
         InlineKeyboardButton(text="👥 Реф.Меню", callback_data="refmenu")],
        [InlineKeyboardButton(text="💾 Чаты", callback_data="chats"),
         InlineKeyboardButton(text="📊 Статистика бота", callback_data="stats")]
            ]
        )
        
        previous_generation_params = {}
        current_state = {}
        messages = {} # Словарь для хранения ID сообщений
        message_to_edit = {}
        
        #Handlers
        @dp.message(Command("start"))
        async def start_command_with_referral(message: types.Message):
            user_id = message.from_user.id
            referrer_id = None
            text = message.text
            username = message.from_user.username or 'UNKNOWN_USER'
            first_name = message.from_user.first_name or 'UNKNOWN_NAME'
            last_name = message.from_user.last_name or 'UNKNOWN_LASTNAME'
            if text and len(text.split()) > 1:
                try:
                    referrer_id = int(text.split()[1])  # Получаем ID пригласившего пользователя
                except ValueError:
                    await message.reply("Неверный формат реферальной ссылки.")
                    return

            async with database_lock:
                try:
                    # Проверяем, зарегистрирован ли пользователь
                    is_registered = await execute_query_single('bot_data.db', "SELECT 1 FROM user_profile WHERE user_id = ?", (user_id,))

                    if is_registered:
                        # Если пользователь уже зарегистрирован, отправляем сообщение
                        await message.reply("Вы уже зарегистрированы.")
                    else:
                        # Если пользователь не зарегистрирован, добавляем его в базу данных
                        await execute_update('bot_data.db', """
                            INSERT INTO user_profile (user_id, username, last_seen, invited_by) VALUES (?, ?, ?, ?)
                        """, (user_id, username.lower() if username else 'UNKNOWN_USER', int(time.time()), referrer_id))
                        await execute_update('bot_data.db', """
                            INSERT INTO users (user_id, username, first_name, last_name) VALUES (?, ?, ?, ?)
                        """, (user_id, username.lower() if username else 'UNKNOWN_USER', first_name, last_name))

                        # Обновляем количество рефералов у пригласившего пользователя
                        if referrer_id:
                            await execute_update('bot_data.db', "UPDATE user_profile SET referrals = referrals + 1 WHERE user_id = ?", (referrer_id,))
                            referrer_info = await get_user(referrer_id)
                            if referrer_info:
                                # Отправляем сообщение о регистрации с реферальной ссылкой
                                await message.reply(f"Вас пригласил пользователь @{referrer_info['username']}. Спасибо за регистрацию!")
                                await bot.send_message(referrer_id, f"Поздравляем! У вас новый реферал @{message.from_user.username}!\nВсего рефералов: {await get_user_referral_count(referrer_id)}")
                                try:
                                    if ADMIN_LOGGING == True:
                                        if IS_SUPERGROUP == True:
                                            await bot.send_message(BOT_LOGS_CHANNEL, f"@{referrer_info['username']} пригласил пользователя @{message.from_user.username}!\nВсего рефералов: {await get_user_referral_count(referrer_id)}", message_thread_id=REGISTER_THREAD)
                                        else:
                                            await bot.send_message(BOT_LOGS_CHANNEL, f"@{referrer_info['username']} пригласил пользователя @{message.from_user.username}!\nВсего рефералов: {await get_user_referral_count(referrer_id)}")
                                    else:
                                        return
                                except TelegramAPIError as e:
                                    logging.exception(f"Произошла ошибка при отправлении лога: {e}")
                        else:
                            await message.reply("Спасибо за регистрацию!")
                            try:
                                if ADMIN_LOGGING == True:
                                    if IS_SUPERGROUP == True:
                                        await bot.send_message(BOT_LOGS_CHANNEL, f"{(user_info := f'@{message.from_user.username}' if message.from_user.username else f'UNKNOWN_USER (ID = <pre>{message.from_user.id}</pre>)')} зарегистрировался в боте", parse_mode=ParseMode.HTML, message_thread_id=REGISTER_THREAD)
                                    else:
                                        await bot.send_message(BOT_LOGS_CHANNEL, f"{(user_info := f'@{message.from_user.username}' if message.from_user.username else f'UNKNOWN_USER (ID = <pre>{message.from_user.id}</>)')} зарегистрировался в боте", parse_mode=ParseMode.HTML)
                                else:
                                    return
                            except TelegramAPIError as e:
                                logging.exception(f"Произошла ошибка при отправлении лога: {e}")
                except Exception as e:
                    logging.exception(f"Ошибка в start_command_with_referral: {e}")
                    await message.reply(f"Ошибка обработки регистрации: {e}")

            is_subscribed = await check_channel_subscription(user_id, pyrogram_client)
            if not is_subscribed:
                await message.reply(f"‼️Для использования бота, подпишитесь на канал {CHANNEL} ‼️")
            message_to_edit[user_id] = await message.reply("ℹ️Напишите запрос боту или перейдите в меню", reply_markup=main_menu_reply_keyboard)
            current_state[user_id] = "main_menu"

        @dp.message(Command("broadcast"))
        async def broadcast_command(message: types.Message):
                user_id = message.from_user.id
                admin_level = await get_admin_level(user_id)
                if admin_level < 4:
                    return await message.reply("У вас нет доступа к этой команде.")
                await show_broadcast_menu(message)

        @dp.callback_query(lambda c: c.data == "show_broadcast_menu")
        async def show_broadcast_menu_callback(call: types.CallbackQuery):
            # Здесь вы можете повторно показать меню рассылок
            broadcasts = await get_broadcasts()  # Получаем список рассылок

            builder = InlineKeyboardBuilder()

            # Добавляем кнопки для каждой рассылки
            for broadcast in broadcasts:
                id, name, enabled = broadcast
                status = "✅" if enabled else "❌"
                builder.button(text=f"{name} {status}", callback_data=f"broadcast_{id}")

            builder.button(text="Создать новую", callback_data="create_broadcast")
            builder.adjust(1)  # Каждая кнопка на отдельной строке, adjust(1) делает то же самое

            await call.message.edit_text("Выберите рассылку для просмотра/редактирования или создайте новую.", reply_markup=builder.as_markup())
            await call.answer()  # Подтверждаем действие

        @dp.callback_query(lambda c: c.data.startswith("broadcast_"))
        async def broadcast_details_callback(call: types.CallbackQuery, state: FSMContext):
            broadcast_id = int(call.data.split("_")[1])
            async with aiosqlite.connect('bot_data.db') as db:
                async with db.execute("SELECT name, text, media_id, media_type, successful, failed, sent, creation_date FROM broadcasts WHERE id = ?", (broadcast_id,)) as cursor:
                    broadcast = await cursor.fetchone()
                    if broadcast:
                        name, text, media_id, media_type, successful, failed, sent, creation_date = broadcast
                        stats = f"Отправлено: {sent}\nУспешно: {successful}\nНеудачно: {failed}"
                        media_str = ""
                        if media_id:
                            media_str = f"\n[Медиафайл присутствует: {media_type}]"
                        else:
                            media_str = "\n[Медиафайл отсутствует]"

                        try:
                            creation_date_dt = datetime.fromisoformat(creation_date)
                            formatted_creation_date = creation_date_dt.strftime('%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            formatted_creation_date = "Дата создания не определена"

                        msg = f"Рассылка: {name}\nДата создания: {formatted_creation_date}\nТекст:\n{text}{media_str}\n\nСтатистика:\n{stats}"

                        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                            [
                                InlineKeyboardButton(text="Редактировать текст", callback_data=f"edit_text_{broadcast_id}"),
                                InlineKeyboardButton(text="Отправить повторно", callback_data=f"resend_broadcast_{broadcast_id}"),
                                InlineKeyboardButton(text="Удалить", callback_data=f"delete_broadcast_{broadcast_id}")
                            ],
                            [
                                InlineKeyboardButton(text="Назад", callback_data="show_broadcast_menu")
                            ]
                        ])
                        await call.message.edit_text(msg, reply_markup=keyboard)
                    else:
                        await call.answer("Рассылка не найдена.")

        @dp.callback_query(lambda c: c.data.startswith("create_broadcast"))
        async def create_broadcast_callback(call: types.CallbackQuery, state: FSMContext):
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Назад", callback_data="cancel_broadcast")]
            ])

            await call.message.edit_text("Введите название рассылки (или нажмите 'Назад' для отмены):", reply_markup=keyboard)
            await state.set_state(BroadcastStates.waiting_for_name)

        # Обработчик для названия рассылки
        @dp.message(StateFilter(BroadcastStates.waiting_for_name))
        async def process_broadcast_name(message: types.Message, state: FSMContext):
            if message.text == "Назад":
                await state.clear()  # Очистка состояния
                await message.reply("Создание рассылки отменено.")
                return

            await state.update_data(broadcast_name=message.text)
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Назад", callback_data="cancel_broadcast")]
            ])

            await message.reply("Введите текст рассылки или перешлите сообщение (или нажмите 'Назад' для отмены). Вы можете прикрепить медиафайл.", reply_markup=keyboard)
            await state.set_state(BroadcastStates.waiting_for_text)

        # Обработчик для текста рассылки
        @dp.message(StateFilter(BroadcastStates.waiting_for_text))
        async def process_broadcast_text(message: types.Message, state: FSMContext):
            broadcast_text = message.text if message.text else message.caption
            await state.update_data(broadcast_text=broadcast_text)

            media_id = None
            media_type = None

            if message.photo:
                media_id = message.photo[-1].file_id
                media_type = "photo"
            elif message.video:
                media_id = message.video.file_id
                media_type = "video"
            elif message.document:
                media_id = message.document.file_id
                media_type = "document"

            if media_id:
                await state.update_data(media_id=media_id, media_type=media_type)

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="Сейчас", callback_data="send_now")],
                [types.InlineKeyboardButton(text="Запланировать", callback_data="schedule_broadcast")],
                [types.InlineKeyboardButton(text="Отмена", callback_data="cancel_broadcast")]
            ])

            await message.reply("Выберите время рассылки:", reply_markup=keyboard)
            await state.set_state(BroadcastStates.waiting_for_time)

        @dp.callback_query(StateFilter(BroadcastStates.waiting_for_time), lambda c: c.data == "send_now")
        async def send_now_callback(call: types.CallbackQuery, state: FSMContext):
            data = await state.get_data()
            logging.info(f"Данные из FSM: {data}")
            broadcast_name = data.get('broadcast_name')
            broadcast_text = data.get('broadcast_text')
            media_id = data.get('media_id')
            media_type = data.get('media_type')
            
            users = await get_all_users()
            success_count = 0
            failed_count = 0
            failed_users = []
            
            for user in users:
                try:
                    username = "@" + user['username']
                    personalized_text = broadcast_text.format(username=username, first_name=user['first_name'], last_name=user['last_name']) if broadcast_text else ""

                    if media_id and media_type == "photo":
                        await bot.send_photo(user['user_id'], media_id, caption=personalized_text)
                    elif media_id and media_type == "video":
                        await bot.send_video(user['user_id'], media_id, caption=personalized_text)
                    elif media_id and media_type == "document":
                        await bot.send_document(user['user_id'], media_id, caption=personalized_text)
                    else:
                        if broadcast_text:
                            await bot.send_message(user['user_id'], personalized_text)
                        else:
                            logging.warning(f"Нечего отправлять пользователю {user['user_id']}: нет ни текста, ни медиа.")
                            continue
                    success_count += 1
                except Exception as e:
                    logging.error(f"Ошибка отправки сообщения пользователю {user['user_id']}: {e}")
                    failed_count += 1
                    failed_users.append(user['user_id'])

            total = success_count + failed_count

            async with aiosqlite.connect('bot_data.db') as db:
                cursor = await db.cursor()
                await cursor.execute(
                    """
                    INSERT INTO broadcasts (name, text, media_type, media_id, creation_date, enabled, successful, failed, sent)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (broadcast_name, broadcast_text, media_type, media_id, datetime.now().isoformat(), 0, success_count, failed_count, total)  # enabled = 1 for "send now"
                )
                broadcast_id = cursor.lastrowid
                await db.commit()
                logging.info(f"Рассылка с ID {broadcast_id} сохранена в БД.")

                try:
                    if ADMIN_LOGGING:
                        log_message = f"Администратор @{call.from_user.username} создал и отправил рассылку с ID {broadcast_id}."
                        if IS_SUPERGROUP:
                            await bot.send_message(BOT_LOGS_CHANNEL, log_message, message_thread_id=ACTION_THREAD)
                        else:
                            await bot.send_message(BOT_LOGS_CHANNEL, log_message)
                    else:
                        return
                except TelegramAPIError as e:
                    logging.exception(f"Произошла ошибка при отправлении лога: {e}")
                #End logging administration activity

            await call.message.edit_text(f"Рассылка завершена!\nУспешно отправлено: {success_count}\nНеудачно отправлено: {failed_count}\nОтправленные пользователя: {', '.join(failed_users)}\n")
            await state.clear()

        @dp.callback_query(lambda c: c.data.startswith("edit_text_"))
        async def edit_broadcast_text_callback(call: types.CallbackQuery, state: FSMContext):
            broadcast_id = int(call.data.split("_")[2])
            async with aiosqlite.connect('bot_data.db') as db:
                async with db.execute("SELECT name, text FROM broadcasts WHERE id = ?", (broadcast_id,)) as cursor:
                    broadcast = await cursor.fetchone()
                    if broadcast:
                        name, text = broadcast
                        await state.update_data(broadcast_id=broadcast_id, broadcast_name=name, broadcast_text=text)
                        await call.message.edit_text(f"Редактирование текста для рассылки '{name}'. Введите новый текст (или /cancel для отмены):")
                        await state.set_state(BroadcastStates.waiting_for_text)
                    else:
                        await call.answer("Рассылка не найдена.")

        @dp.callback_query(lambda c: c.data.startswith("resend_broadcast_"))
        async def resend_broadcast_callback(call: types.CallbackQuery):
            broadcast_id = int(call.data.split("_")[2])
            try:
                # Logging administration activity
                if ADMIN_LOGGING:
                    log_message = f"Администратор @{call.from_user.username} повторно отправил рассылку с ID {broadcast_id}."
                    if IS_SUPERGROUP:
                        await bot.send_message(BOT_LOGS_CHANNEL, log_message, message_thread_id=ACTION_THREAD)
                    else:
                        await bot.send_message(BOT_LOGS_CHANNEL, log_message)
            except TelegramAPIError as e:
                logging.exception(f"Произошла ошибка при отправлении лога: {e}")
            #End logging administration activity
            await send_broadcast(broadcast_id)
            await call.answer("Рассылка отправлена повторно.")

        @dp.callback_query(lambda c: c.data.startswith("delete_broadcast_"))
        async def delete_broadcast_callback(call: types.CallbackQuery, state: FSMContext):
            broadcast_id = int(call.data.split("_")[2])
            async with aiosqlite.connect('bot_data.db') as db:
                await db.execute("DELETE FROM broadcasts WHERE id = ?", (broadcast_id,))
                await db.commit()

            await call.message.edit_text("Рассылка удалена.")
            await show_broadcast_menu(call.message)

        @dp.callback_query(lambda c: c.data == "cancel_broadcast")
        async def cancel_broadcast_callback(call: types.CallbackQuery, state: FSMContext):
            await call.message.edit_text("Создание рассылки отменено.")
            await state.clear()

        @dp.message(Command("stats"))
        async def stats_command(message: types.Message):
                    try:
                        # Время работы бота (пример: предполагается, что start_time хранится в переменной)
                        start_time = datetime.now() - timedelta(days=2) # пример, заменить на реальное значение
                        uptime = datetime.now() - start_time
                        uptime_str = str(uptime).split('.')[0]

                        # Количество моделей (подсчёт моделей во всех словарях API_PROVIDERS)
                        # Подсчет уникальных моделей
                        unique_models = set()
                        for provider in API_PROVIDERS.values():
                            unique_models.update(provider["models"])

                        # Выводим уникальные модели в консоль для проверки
                        if ENGEENER_LOGS:
                            logging.info(f"Уникальные модели: {unique_models}")

                        model_count = len(unique_models)  # Количество уникальных моделей

                        # Общее количество ответов (из базы данных)
                        total_responses = await execute_query_single('bot_data.db', "SELECT SUM(requests_count) FROM user_profile")
                        total_responses = total_responses[0] if total_responses else 0

                        # Количество пользователей (из базы данных)
                        user_count = await execute_query_single('bot_data.db', "SELECT COUNT(*) FROM users")
                        user_count = user_count[0] if user_count else 0

                        # Приблизительное количество сообщений в БД
                        approx_message_count = (await execute_query_single('_history.db', "SELECT COUNT(*) FROM messages"))[0] // 2

                        # Текст сообщения со статистикой
                        stats_text = f"""
                        📊 <b>Статистика бота {BOT_NAME}:</b>

⏳ <b>Работает:</b> {uptime_str}
🤖 <b>Количество моделей:</b> {model_count}
💬 <b>Общее количество запросов:</b> {total_responses}
👤 <b>Количество пользователей:</b> {user_count}
✉️ <b>Приблизительное количество сообщений в БД:</b> {approx_message_count}
                        """

                        # Кнопки для топов (остаются без изменений)
                        keyboard = InlineKeyboardMarkup(
                            inline_keyboard=[
                                [InlineKeyboardButton(text="Топ по запросам", callback_data="top_requests"),
                                 InlineKeyboardButton(text="Топ по рефералам", callback_data="top_referrals")],
                                [InlineKeyboardButton(text="Топ по балансу", callback_data="top_balance")],
                                [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]
                            ]
                        )

                        await message.reply(stats_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
                    except Exception as e:
                        await message.reply(f"Ошибка при получении статистики: {e}")
                        logging.exception(f"Ошибка в stats_command: {e}")       

        @dp.callback_query(lambda q: q.data == "stats")
        async def stats_callback(call: types.CallbackQuery):
                    try:
                        start_time = datetime.now() - timedelta(days=2)  # Замените на ваш способ получения времени запуска бота
                        uptime = datetime.now() - start_time
                        uptime_str = str(uptime).split('.')[0]

                        unique_models = set()
                        for provider in API_PROVIDERS.values():
                            unique_models.update(provider["models"])

                        model_count = len(unique_models)

                        total_responses = await execute_query_single('bot_data.db', "SELECT SUM(requests_count) FROM user_profile")
                        total_responses = total_responses[0] if total_responses else 0

                        user_count = await execute_query_single('bot_data.db', "SELECT COUNT(*) FROM users")
                        user_count = user_count[0] if user_count else 0

                        approx_message_count = (await execute_query_single('_history.db', "SELECT COUNT(*) FROM messages"))[0] // 2

                        stats_text = f"""
                        📊 <b>Статистика бота {BOT_NAME}:</b>

⏳ <b>Работает:</b> {uptime_str}
🤖 <b>Количество моделей:</b> {model_count}
💬 <b>Общее количество запросов:</b> {total_responses}
👤 <b>Количество пользователей:</b> {user_count}
✉️ <b>Приблизительное количество сообщений в БД:</b> {approx_message_count}
                        """

                        keyboard = InlineKeyboardMarkup(
                            inline_keyboard=[
                                [InlineKeyboardButton(text="Топ по запросам", callback_data="top_requests")],
                                [InlineKeyboardButton(text="Топ по рефералам", callback_data="top_referrals")],
                                [InlineKeyboardButton(text="Топ по балансу", callback_data="top_balance")],
                                [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]
                            ]
                        )

                        await call.message.edit_text(stats_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

                    except Exception as e:
                        await call.answer("Ошибка при получении статистики.")
                        logging.exception(f"Ошибка в stats_callback: {e}")
               
        @dp.callback_query(lambda q: q.data == "top_referrals")
        async def top_referrals_callback(call: types.CallbackQuery):
                    try:
                        top_users = await execute_query('bot_data.db', "SELECT username, referrals FROM user_profile ORDER BY referrals DESC LIMIT 10")
                        top_referrals_text = "<b>Топ 10 пользователей по количеству рефералов:</b>\n"
                        for i, (username, referrals) in enumerate(top_users):
                            place_indicator = get_place_indicator(i + 1)
                            formatted_username = f"@{username}" if username else "UnknownUser"
                            top_referrals_text += f"<b>{place_indicator}</b> <i>{formatted_username}</i>: {referrals}\n"

                        await call.message.edit_text(top_referrals_text, parse_mode=ParseMode.HTML,
                                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад", callback_data="stats")]]))

                    except Exception as e:
                        await call.answer("Ошибка при получении топа рефералов.")
                        logging.exception(f"Ошибка в top_referrals_callback: {e}")


        @dp.callback_query(lambda q: q.data == "top_balance")
        async def top_balance_callback(call: types.CallbackQuery):
                    try:
                        top_users = await execute_query('bot_data.db', "SELECT username, balance FROM user_profile ORDER BY balance DESC LIMIT 10")
                        top_balance_text = "<b>Топ 10 пользователей по балансу:</b>\n"
                        for i, (username, balance) in enumerate(top_users):
                            place_indicator = get_place_indicator(i + 1)
                            formatted_username = f"@{username}" if username else "UnknownUser"
                            top_balance_text += f"<b>{place_indicator}</b> <i>{formatted_username}</i>: {balance}\n"
                        
                        await call.message.edit_text(top_balance_text, parse_mode=ParseMode.HTML,
                                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад", callback_data="stats")]]))
                        
                    except Exception as e:
                        await call.answer("Ошибка при получении топа баланса.")
                        logging.exception(f"Ошибка в top_balance_callback: {e}")
     
        @dp.callback_query(lambda q: q.data == "top_requests")
        async def top_requests_callback(call: types.CallbackQuery):
                    try:
                        top_users = await execute_query('bot_data.db', "SELECT username, requests_count FROM user_profile ORDER BY requests_count DESC LIMIT 10")

                        top_requests_text = "<b>Топ 10 пользователей по количеству запросов:</b>\n"
                        for i, (username, count) in enumerate(top_users):
                            place_indicator = get_place_indicator(i + 1)
                            formatted_username = f"@{username}" if username else "UnknownUser"
                            top_requests_text += f"<b>{place_indicator}</b> <i>{formatted_username}</i>: {count}\n"

                        await call.message.edit_text(top_requests_text, parse_mode=ParseMode.HTML,
                                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад", callback_data="stats")]]))

                    except Exception as e:
                        await call.answer("Ошибка при получении топа запросов.")
                        logging.exception(f"Ошибка в top_requests_callback: {e}")


        def get_place_indicator(place: int):
                    """Возвращает эмодзи для места в рейтинге."""
                    if place == 1:
                        return "🥇"
                    elif place == 2:
                        return "🥈"
                    elif place == 3:
                        return "🥉"
                    else:
                        return f"{place}."
                        
        @dp.callback_query(lambda query: query.data in ["profile", "clear_history", "refmenu", "model_selection", "img_model_selection", "stats"])
        async def menu_callback(query: types.CallbackQuery):
            user_id = query.from_user.id
            try:
                if query.data == "profile":
                    await show_profile_edit(query.message, user_id)
                    current_state[user_id] = "profile"
                elif query.data == "clear_history":
                    await clear_context(user_id)
                    await query.answer("История очищена!")
                    current_state[user_id] = "history"
                elif query.data == "refmenu":
                    await ref_menu(query.message, user_id)
                    current_state[user_id] = "refmenu"
                elif query.data == "model_selection":
                    models_keyboard = create_models_keyboard()
                    await query.message.edit_text("Выберите модель:", reply_markup=models_keyboard)
                    current_state[user_id] = "model_selection"
                elif query.data == "img_model_selection":
                    await query.message.edit_text("Выберите модель для изображения:", reply_markup=img_models_keyboard)
                    current_state[user_id] = "img_model_selection"
                elif query.data == "stats":
                    await stats_callback(query.message, user_id)
                    current_state[user_id] = "stats"
                await query.answer()
            except Exception as e:
                logging.exception(f"Ошибка в menu_callback: {e}")
                await query.answer("Произошла ошибка. Попробуйте позже.")
                

        @dp.callback_query(lambda query: query.data == "main_menu")
        async def back_to_main_menu(query: types.CallbackQuery):
            try:
                await query.message.edit_text("Главное меню:", reply_markup=main_menu_keyboard)
                current_state[query.from_user.id] = "main_menu"
                await query.answer() # Добавлено для подтверждения действия
            except Exception as e:
                logging.exception(f"Ошибка в back_to_main_menu: {e}")
                await query.answer("Произошла ошибка. Попробуйте позже.")

        @dp.callback_query(lambda query: query.data.startswith("set_img_model:"))
        async def set_img_model_callback(query: types.CallbackQuery):
            img_model_name = query.data.split(":")[1]
            try:
                await set_image_model(query.from_user.id, img_model_name)
                await query.answer(f"Модель изображения успешно изменена на {img_model_name}")
                await query.message.edit_text(f"Модель изображения успешно изменена на {img_model_name}", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=back_txt, callback_data="main_menu")]]))
                current_state[query.from_user.id] = "img_model_selection"
            except Exception as e:
                logging.exception(f"Ошибка в set_img_model_callback: {e}")
                await query.answer("Произошла ошибка. Попробуйте позже.")
                
                
        # Обработчик для кнопки "💾 Чаты"
        @dp.callback_query(lambda query: query.data == "chats")
        async def chats_callback(query: types.CallbackQuery):
            user_id = query.from_user.id
            chats_keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="📥 Загрузить чат", callback_data="import_chat")],
                    [InlineKeyboardButton(text="📤 Получить чат", callback_data="export_chat")],
                    [InlineKeyboardButton(text=back_txt, callback_data="main_menu")],
                ]
            )
            await query.message.edit_text("Меню Чатов:", reply_markup=chats_keyboard)
            current_state[user_id] = "chats"
	
        @dp.message(Command("ref"))
        async def ref_command(message: types.Message):
            user_id = message.from_user.id
            ref_link = f"http://t.me/{BOT_USERNAME}?start={user_id}"
            try:
                await message.reply(f"Ваша реферальная ссылка: {ref_link}", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=back_txt, callback_data="main_menu")]]))
            except Exception as e:
                logging.exception(f"Ошибка в ref_command: {e}")
                await message.reply(f"Произошла ошибка: {e}")        
       
        @dp.callback_query(lambda c: c.data == "export_chat")
        async def export_chat_callback(call: types.CallbackQuery):
            user_id = call.from_user.id
            try:
                async with file_lock:
                    file_path = await export_chat_history(user_id, pyrogram_client)

                if file_path:
                    try:
                        await call.message.answer("Отправляю историю чата...")
                        await call.bot.send_document(user_id, FSInputFile(file_path), caption=f"history_{user_id}.json")
                        await call.answer("История чата отправлена!")
                        os.remove(file_path)
                    except errors.RPCError as e:
                        await call.message.answer(f"Ошибка Telegram API: {e}")
                        logging.exception(f"Ошибка Telegram API: {e}")
                        os.remove(file_path)
                    except Exception as e:
                        await call.message.answer(f"Ошибка отправки файла: {e}")
                        logging.exception(f"Ошибка отправки файла: {e}")
                        os.remove(file_path)
                else:
                    await call.message.answer("Ошибка: данные не подготовлены или пусты.")
            except Exception as e:
                await call.message.answer(f"Произошла ошибка: {e}")
                logging.exception(f"Ошибка в export_chat_callback: {e}")
        
        @dp.callback_query(lambda query: query.data == "import_chat")
        async def importing_chat_callback(call: types.CallbackQuery):
            await call.message.reply("Отправьте файл history.json:")
            user_id = call.from_user.id
            current_state[user_id] = {"state": "awaiting_file"}  # Новое состояние

        @dp.message(lambda message: current_state.get(message.from_user.id) == "awaiting_file")
        async def handle_file_upload(message: types.Message):
            user_id = message.from_user.id
            if message.content_type == ContentType.DOCUMENT:
                file_id = message.document.file_id
                current_state[user_id]["state"] = "processing_file"
                current_state[user_id]["file_id"] = file_id #Сохраняем ID файла в состоянии
                try:
                    await message.reply("Обработка файла...")
                    file_bytes = await bot.download_file(file_id)
                    json_data = file_bytes.decode('utf-8', errors='ignore')
                    try:
                        json.loads(json_data)
                        if await import_chat_history(user_id, json_data):
                            await message.reply("Чат успешно загружен!")
                        else:
                            await message.reply("Ошибка импорта истории чата.")
                    except json.JSONDecodeError:
                        await message.reply("Файл не является корректным JSON.")
                    del current_state[user_id] # удаляем пользователя из состояния
                except Exception as e:
                    await message.reply(f"Произошла ошибка: {e}")
            else:
                await message.reply("Пожалуйста, отправьте файл.")
            
        @dp.callback_query(lambda query: query.data.startswith("set_model:"))
        async def set_model_callback(query: types.CallbackQuery):
            model_name = query.data.split(":")[1]
            try:
                await set_user_model(query.from_user.id, model_name)
                await query.answer(f"Модель успешно изменена на {model_name}")
                await query.message.edit_text(f"Модель успешно изменена на {model_name}", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=back_txt, callback_data="main_menu")]]))
                current_state[query.from_user.id] = "model_selection"
            except Exception as e:
                logging.exception(f"Ошибка в set_model_callback: {e}")
                await query.answer("Произошла ошибка. Попробуйте позже.")
                
        async def get_user_profile(user_id):
                result = await execute_query_single('bot_data.db', """
                    SELECT 
                    img_model, model, balance, referrals, last_seen, invited_by, requests_count
                    FROM user_profile
                    WHERE user_id = ?
                """, (user_id,))
                return result if result else None  # Return None if profile not found
                
        async def ref_menu(message: types.Message, user_id):
            ref_link = f"http://t.me/{BOT_USERNAME}?start={user_id}"
            try:
                await message.edit_text(f"Ваша реферальная ссылка: {ref_link}", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=back_txt, callback_data="main_menu")]]))
            except Exception as e:
                logging.exception(f"Ошибка в ref_menu: {e}")
                await message.reply(f"Произошла ошибка: {e}")

        async def show_profile_menu(query_message, user_id):
            message_returned = await show_profile_edit(user_id)
            await message_returned.edit_reply_markup(InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=back_txt, callback_data="main_menu")]]))


        async def get_ban_info(user_id):
            """Получает информацию о бане пользователя."""
            result = await execute_query_single('bot_data.db', "SELECT ban_until, ban_reason, banned_by FROM banned_users WHERE user_id = ?", (user_id,))
            if result:
                 ban_until, ban_reason, banned_by = result
                 banned_by_user = await get_user(banned_by)  # Получаем информацию о пользователе, который забанил
                 banned_by_username = banned_by_user['username'] if banned_by_user else "Unknown"
                 return {
                    "ban_until": ban_until,
                    "ban_reason": ban_reason,
                    "banned_by": banned_by_username
                }
            return None


        async def get_admin_info(user_id):
            """Получает информацию о статусе администратора."""
            result = await execute_query_single('bot_data.db', "SELECT level FROM admins WHERE user_id = ?", (user_id,))
            return result[0] if result else 0


        async def show_profile_edit(message: types.Message, user_id: int):
            try:
                profile_data = await get_user_profile(user_id)
                user_data = await get_user(user_id)
                ban_info = await get_ban_info(user_id)
                admin_level = await get_admin_info(user_id)

                if profile_data:
                    img_model, model, balance, referrals, last_seen, invited_by, requests_count = profile_data
                    last_seen_datetime = datetime.fromtimestamp(last_seen)

                    invited_by_text = "Неизвестно"  # Значение по умолчанию
                    if invited_by:
                        invited_by_user = await get_user(invited_by)
                        invited_by_username = invited_by_user['username']
                        invited_by_text = f"@{invited_by_user['username']}" if invited_by_user else "Неизвестно"
                    else:
                        invited_by_text = "Никто" 
                    profile_text = f"""👀 Профиль пользователя @{user_data['username']}:
🪪 Имя: {user_data['first_name']} | {user_data['last_name']}
🪪 Username: @{user_data['username']}
🆔 {user_id}
🤖 ChatGPT-Модель: {model}
🖼️ Image Модель: {img_model}
🪙 Баланс: {balance}
👥 Рефералы: {referrals}
🪄 Количество запросов: {requests_count}
👤 Пригласил: {invited_by_text}
🕒 Последний визит:
{last_seen_datetime.strftime('%Y-%m-%d %H:%M:%S')}"""

                    if ban_info:
                        ban_until_datetime = datetime.fromtimestamp(ban_info["ban_until"]) if ban_info["ban_until"] != -1 else None
                        profile_text += f"""
Бан:
    ⏰ До:
    {ban_until_datetime.strftime('%Y-%m-%d %H:%M:%S') if ban_until_datetime else 'Навсегда'}
    💬 Причина: {ban_info["ban_reason"]}
    👮‍♂️ Забанил: @{ban_info["banned_by"]}"""

                    if admin_level > 0:
                        profile_text += f"""
🛡️ Администратор: ✅
🔑 Уровень доступа: {admin_level}"""


                    await message.edit_text(profile_text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=back_txt, callback_data="main_menu")]]))
                else:
                    await message.reply("❌ Профиль не найден. Пользователь не зарегистрирован.")
                    print(f"Профиль для user_id={user_id} не найден. Проверьте таблицу user_profile in bot_data.db.")

            except aiosqlite.Error as e:
                await message.reply(f"Ошибка базы данных: {e}")
                logging.exception(f"Ошибка базы данных: {e}") # Log the exception for debugging
            except TelegramAPIError as e:
                await message.reply(f"Ошибка Telegram API: {e}")
                logging.exception(f"Ошибка Telegram API: {e}") # Log the exception for debugging
            except Exception as e:
                await message.reply(f"Произошла ошибка: {e}")
                logging.exception(f"Произошла ошибка: {e}") # Log the exception for debugging

        async def show_profile(message: types.Message, user_id: int):
            try:
                profile_data = await get_user_profile(user_id)
                user_data = await get_user(user_id)
                ban_info = await get_ban_info(user_id)
                admin_level = await get_admin_info(user_id)

                if profile_data:
                    img_model, model, balance, referrals, last_seen, invited_by, requests_count = profile_data
                    last_seen_datetime = datetime.fromtimestamp(last_seen)

                    invited_by_text = "Неизвестно"  # Значение по умолчанию
                    if invited_by:
                        invited_by_user = await get_user(invited_by)
                        invited_by_text = f"@{invited_by_user['username']}" if invited_by_user else "Неизвестно"
                    else:
                        invited_by_text = "Никто" 
                    profile_text = f"""👀 Профиль пользователя @{user_data['username']}:
🪪 Имя: {user_data['first_name']} | {user_data['last_name']}
🪪 Username: @{user_data['username']}
🆔 {user_id}
🤖 ChatGPT-Модель: {model}
🖼️ Image Модель: {img_model}
🪙 Баланс: {balance}
👥 Рефералы: {referrals}
🪄 Количество запросов: {requests_count}
👤 Пригласил: {invited_by_text}
🕒 Последний визит:
{last_seen_datetime.strftime('%Y-%m-%d %H:%M:%S')}"""

                    if ban_info:
                        ban_until_datetime = datetime.fromtimestamp(ban_info["ban_until"]) if ban_info["ban_until"] != -1 else None
                        profile_text += f"""
Бан:
    ⏰ До:
    {ban_until_datetime.strftime('%Y-%m-%d %H:%M:%S') if ban_until_datetime else 'Навсегда'}
    💬 Причина: {ban_info["ban_reason"]}
    👮‍♂️ Забанил: @{ban_info["banned_by"]}"""

                    if admin_level > 0:
                        profile_text += f"""
🛡️ Администратор: ✅
🔑 Уровень доступа: {admin_level}"""


                    await message.reply(profile_text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=back_txt, callback_data="main_menu")]]))
                else:
                    await message.reply("❌ Профиль не найден. Пользователь не зарегистрирован.")
                    print(f"Профиль для user_id={user_id} не найден. Проверьте таблицу user_profile in bot_data.db.")

            except aiosqlite.Error as e:
                await message.reply(f"Ошибка базы данных: {e}")
                logging.exception(f"Ошибка базы данных: {e}") # Log the exception for debugging
            except TelegramAPIError as e:
                await message.reply(f"Ошибка Telegram API: {e}")
                logging.exception(f"Ошибка Telegram API: {e}") # Log the exception for debugging
            except Exception as e:
                await message.reply(f"Произошла ошибка: {e}")
                logging.exception(f"Произошла ошибка: {e}") # Log the exception for debugging
                
        @dp.message(Command("profile"))
        async def profile_command(message: types.Message):
            user_id = message.from_user.id
            args = message.text.split()

            if len(args) == 1:  # /profile (показать свой профиль)
                await show_profile(message, user_id)
            elif len(args) == 3 and args[1] == "show":  # /profile show <id|@username>
                try:
                    # Проверяем уровень доступа
                    admin_level = await get_admin_level(user_id)
                    if admin_level < 1:
                        return await message.reply("У вас нет прав для просмотра профиля других пользователей.")

                    user_id = await get_user_id(args[2], bot)
                    if user_id is None:
                        await message.reply("Пользователь не найден.")
                        return
                    await show_profile(message, user_id)
                except Exception as e:
                    await message.reply(f"Ошибка: {e}")
            else:
                await message.reply("Неверный формат команды. Используйте /profile или /profile show <id|@username> (для админов 1 уровня)")

        @dp.message(Command('ban_info'))
        async def ban_info(message: types.Message):
            try:
                result = await execute_query_single('bot_data.db', "SELECT ban_until, ban_reason FROM banned_users WHERE user_id = ?", (message.from_user.id,))
                if result:
                    ban_until, ban_reason = result
                    await message.reply(f"{'Вы забанены навсегда.' if ban_until == -1 else f'Вы забанены до {datetime.fromtimestamp(ban_until)} по причине: {ban_reason}. Осталось времени: {format_time_left(ban_until)}.'}")
                else:
                    await message.reply("Вы не забанены.")
            except Exception as e:
                logging.exception(f"Ошибка в ban_info: {e}")
                await message.reply(f"Произошла ошибка: {e}")

        # Add /stat command for admins level 4
        @dp.message(Command("stat"))
        async def stat_command(message: types.Message):
            admin_level = await get_admin_level(message.from_user.id)
            if admin_level < 4:
                return await message.reply("У вас нет прав.")

            args = message.text.split()
            if len(args) < 3:
                return await message.reply("Неверный формат команды.  Используйте: /stat balance|ref add|remove|set|reset <id|@username> <value>")

            what = args[1].lower()
            action = args[2].lower()
            if what not in ["balance", "ref"]:
                return await message.reply("Неверный параметр. Используйте balance или ref.")
            if action not in ["add", "remove", "set", "reset"]:
                return await message.reply("Неверная операция. Используйте add, remove, set или reset.")


            if len(args) < 4:
                return await message.reply("Не указан пользователь или значение.")

            try:
                user_id = await get_user_id(args[3], bot)
                if user_id is None:
                    return await message.reply("Пользователь не найден.")
                # Проверка прав взаимодействия
                if not await can_admin_interact(message.from_user.id, user_id):
                    return await message.reply("Вы не можете взаимодействовать с этим администратором.")

                value = 0
                if action != "reset":
                  try:
                    value = int(args[4])
                  except (ValueError, IndexError):
                    return await message.reply("Неверное значение.")

                async with database_lock:
                    if what == "balance":
                        if action == "add":
                            try:
                                if ADMIN_LOGGING == True:
                                    if IS_SUPERGROUP == True:
                                        await bot.send_message(BOT_LOGS_CHANNEL, f"@{message.from_user.username} увеличил на {value} баланс пользователя {args[3]}", message_thread_id=ACTION_THREAD)
                                    else:
                                        await bot.send_message(BOT_LOGS_CHANNEL, f"@{message.from_user.username} увеличил на {value} баланс пользователя {args[3]}")
                                else:
                                    return
                            except TelegramAPIError as e:
                                logging.exception(f"Произошла ошибка при отправлении лога: {e}")
                            await execute_update('bot_data.db', "UPDATE user_profile SET balance = balance + ? WHERE user_id = ?", (value, user_id))
                            await bot.send_message(user_id, f"вам было начислено {value} монет на баланс от администратора @{message.from_user.username}")
                            await bot.send_message(message.from_user.id, f"Вы начислили {value} монет на баланс пользователю {args[3]}")
                        elif action == "remove":
                            try:
                                if ADMIN_LOGGING == True:
                                    if IS_SUPERGROUP == True:
                                        await bot.send_message(BOT_LOGS_CHANNEL, f"@{message.from_user.username} уменьшил на {value} баланс пользователя {args[3]}", message_thread_id=ACTION_THREAD)
                                    else:
                                        await bot.send_message(BOT_LOGS_CHANNEL, f"@{message.from_user.username} уменьшил на {value} баланс пользователя {args[3]}")
                                else:
                                    return
                            except TelegramAPIError as e:
                                logging.exception(f"Произошла ошибка при отправлении лога: {e}")
                            await execute_update('bot_data.db', "UPDATE user_profile SET balance = balance - ? WHERE user_id = ?", (value, user_id))
                            bot.send_message(user_id, f"У вас снял {value} монет с баланса администратор @{message.from_user.username}")
                            bot.send_message(message.from_user.id, f"Вы сняли {value} монет с баланса пользователя {args[3]}")
                        elif action == "set":
                            try:
                                if ADMIN_LOGGING == True:
                                    if IS_SUPERGROUP == True:
                                        await bot.send_message(BOT_LOGS_CHANNEL, f"@{message.from_user.username} установил на {value} баланс пользователя {args[3]}", message_thread_id=ACTION_THREAD)
                                    else:
                                        await bot.send_message(BOT_LOGS_CHANNEL, f"@{message.from_user.username} установил на {value} баланс пользователя {args[3]}")
                                else:
                                    return
                            except TelegramAPIError as e:
                                logging.exception(f"Произошла ошибка при отправлении лога: {e}")
                            await execute_update('bot_data.db', "UPDATE user_profile SET balance = ? WHERE user_id = ?", (value, user_id))
                            bot.send_message(user_id, f"вам установлен баланс в {value} монет администратором @{message.from_user.username}")
                            bot.send_message(message.from_user.id, f"Вы устновили баланс в {value} монет пользователю {args[3]}")
                        elif action == "reset":
                            try:
                                if ADMIN_LOGGING == True:
                                    if IS_SUPERGROUP == True:
                                        await bot.send_message(BOT_LOGS_CHANNEL, f"@{message.from_user.username} обнулил баланс пользователя {args[3]}", message_thread_id=ACTION_THREAD)
                                    else:
                                        await bot.send_message(BOT_LOGS_CHANNEL, f"@{message.from_user.username} обнулил баланс пользователя {args[3]}")
                                else:
                                    return
                            except TelegramAPIError as e:
                                logging.exception(f"Произошла ошибка при отправлении лога: {e}")
                            await execute_update('bot_data.db', "UPDATE user_profile SET balance = 0 WHERE user_id = ?", (user_id,))
                            bot.send_message(user_id, f"вам обнулил баланс администратор @{message.from_user.username}")
                            bot.send_message(message.from_user.id, f"Вы обнулили баланс пользователю {args[3]}")
                    elif what == "ref":
                        if action == "add":
                            try:
                                if ADMIN_LOGGING == True:
                                    if IS_SUPERGROUP == True:
                                        await bot.send_message(BOT_LOGS_CHANNEL, f"@{message.from_user.username} увеличил на {value} количество рефералов у пользователя {args[3]}", message_thread_id=ACTION_THREAD)
                                    else:
                                        await bot.send_message(BOT_LOGS_CHANNEL, f"@{message.from_user.username} увеличил на {value} количество рефералов у пользователя {args[3]}")
                                else:
                                    return
                            except TelegramAPIError as e:
                                logging.exception(f"Произошла ошибка при отправлении лога: {e}")
                            await execute_update('bot_data.db', "UPDATE user_profile SET referrals = referrals + ? WHERE user_id = ?", (value, user_id))
                            bot.send_message(user_id, f"вам было добавлено {value} рефералов от администратора @{message.from_user.username}")
                            bot.send_message(message.from_user.id, f"Вы начислили {value} рефералов пользователю {args[3]}")
                        elif action == "remove":
                            try:
                                if ADMIN_LOGGING == True:
                                    if IS_SUPERGROUP == True:
                                        await bot.send_message(BOT_LOGS_CHANNEL, f"@{message.from_user.username} уменьшил на {value} количество рефералов у пользователя {args[3]}", message_thread_id=ACTION_THREAD)
                                    else:
                                        await bot.send_message(BOT_LOGS_CHANNEL, f"@{message.from_user.username} уменьшил на {value} количество рефералов у пользователя {args[3]}")
                                else:
                                    return
                            except TelegramAPIError as e:
                                logging.exception(f"Произошла ошибка при отправлении лога: {e}")
                            await execute_update('bot_data.db', "UPDATE user_profile SET referrals = referrals - ? WHERE user_id = ?", (value, user_id))
                            bot.send_message(user_id, f"У вас было снято {value} рефералов администратором @{message.from_user.username}")
                            bot.send_message(message.from_user.id, f"Вы сняли {value} рефералов у пользователя {args[3]}")
                        elif action == "set":
                            try:
                                if ADMIN_LOGGING == True:
                                    if IS_SUPERGROUP == True:
                                        await bot.send_message(BOT_LOGS_CHANNEL, f"@{message.from_user.username} установил на {value} количество рефералов у пользователя {args[3]}", message_thread_id=ACTION_THREAD)
                                    else:
                                        await bot.send_message(BOT_LOGS_CHANNEL, f"@{message.from_user.username} установил на {value} количество рефералов у пользователя {args[3]}")
                                else:
                                    return
                            except TelegramAPIError as e:
                                logging.exception(f"Произошла ошибка при отправлении лога: {e}")
                            await execute_update('bot_data.db', "UPDATE user_profile SET referrals = ? WHERE user_id = ?", (value, user_id))
                            bot.send_message(user_id, f"Вам установлено на {value} кол-во рефералов администратором @{message.from_user.username}")
                            bot.send_message(message.from_user.id, f"Вы установили {value} рефералов у пользователя {args[3]}")
                        elif action == "reset":
                            try:
                                if ADMIN_LOGGING == True:
                                    if IS_SUPERGROUP == True:
                                        await bot.send_message(BOT_LOGS_CHANNEL, f"@{message.from_user.username} обнулил количество рефералов у пользователя {args[3]}", message_thread_id=ACTION_THREAD)
                                    else:
                                        await bot.send_message(BOT_LOGS_CHANNEL, f"@{message.from_user.username} обнулил количество рефералов у пользователя {args[3]}")
                                else:
                                    return
                            except TelegramAPIError as e:
                                logging.exception(f"Произошла ошибка при отправлении лога: {e}")
                            await execute_update('bot_data.db', "UPDATE user_profile SET referrals = 0 WHERE user_id = ?", (user_id,))
                            bot.send_message(user_id, f"Вам обнулил кол-во рефералов администратор @{message.from_user.username}")
                            bot.send_message(message.from_user.id, f"Вы обнулили кол-во рефералов у пользователя {args[3]}")

            except Exception as e:
                await message.reply(f"Ошибка: {e}")

        dp.message.register(ban_user, Command("ban"))

        dp.message.register(unban_user, Command("unban"))

        @dp.message(Command("admin"))
        async def admin_command(message: types.Message):
            admin_level = await get_admin_level(message.from_user.id)
            if admin_level < 3:  # Только админы 3 уровня и выше могут использовать эту команду
                return await message.reply("У вас нет прав.")

            args = message.text.split()
            if len(args) < 2:
                return await message.reply("Недостаточно аргументов. Используйте: /admin <action> <@username|user_id> [level|value]")

            action = args[1].lower()

            if action in ["add", "remove", "setlevel"]:
                await manage_admins(message, action, args[2:])
            elif action == "list":
                await list_admins(message)
            else:
                await message.reply("Неверная операция. Используйте: add, remove, list, setlevel")


        async def manage_admins(message: types.Message, action: str, args: list):
            if len(args) < 1:
                return await message.reply("Не указан пользователь.")

            try:
                user_id = await get_user_id(args[0], bot)
                if user_id is None:
                    return await message.reply("Пользователь не найден.")

                user_name = args[0]

                if action == "add":
                    level = int(args[1]) if len(args) > 1 and 1 <= int(args[1]) <= 4 else 1  # Уровень по умолчанию 1
                    user_info = await get_user(user_id)
                    username = user_info["username"]
                    if username:
                        await add_admin(message, user_id, level)
                        await bot.send_message(message.from_user.id, f"Пользователь {user_name} добавлен в список администраторов.")
                        await bot.send_message(user_id, f"Вы были добавлены в список администраторов бота с уровнем доступа {level} пользователем @{message.from_user.username}")
                        try:
                            if ADMIN_LOGGING == True:
                                if IS_SUPERGROUP == True:
                                    await bot.send_message(BOT_LOGS_CHANNEL, f"Пользователь с ID {user_name} был добавлен в список администраторов с уровнем {level} пользователем @{message.from_user.username}", message_thread_id=ACTION_THREAD)
                                else:
                                    await bot.send_message(BOT_LOGS_CHANNEL, f"Пользователь с ID {user_name} был добавлен в список администраторов с уровнем {level} пользователем @{message.from_user.username}")
                            else:
                                return
                        except TelegramAPIError as e:
                            logging.exception(f"Произошла ошибка при отправлении лога: {e}")
                    else:
                        bot.send_message(message.from_user.id, "У пользователя должен быть установлен юзернейм")
                elif action == "remove":
                    await remove_admin(message, user_id)
                    await bot.send_message(message.from_user.id, f"Пользователь @{user_name} удалён из списка администраторов")
                    await bot.send_message(user_id, f"Вы были удалены из списка администраторов пользователем @{message.from_user.username}")
                    try:
                        if ADMIN_LOGGING == True:
                            if IS_SUPERGROUP == True:
                                await bot.send_message(BOT_LOGS_CHANNEL, f"Пользователь с ID {user_name} был удалён из списка администраторов пользователем @{message.from_user.username}", message_thread_id=ACTION_THREAD)
                            else:
                                await bot.send_message(BOT_LOGS_CHANNEL, f"Пользователь с ID {user_name} был удалён из списка администраторов пользователем @{message.from_user.username}")
                        else:
                            return
                    except TelegramAPIError as e:
                        logging.exception(f"Произошла ошибка при отправлении лога: {e}")
                elif action == "setlevel":
                    if len(args) < 2:
                        return await message.reply("Не указан уровень доступа.")
                    try:
                        level = int(args[1])
                        if not 1 <= level <= 4:
                            return await message.reply("Уровень доступа должен быть от 1 до 4.")
                        await set_admin_level(message, user_id, level)
                        await bot.send_message(message.from_user.id, f"Вы изменили уровень доступа администратору @{user_name} на {level}")
                        await bot.send_message(user_id, f"Ваш уровень доступа был изменён на {level} пользователем @{message.from_user.username}")
                    except ValueError:
                        await message.reply("Неверный формат уровня доступа.")
                    try:
                        if ADMIN_LOGGING == True:
                            if IS_SUPERGROUP == True:
                                await bot.send_message(BOT_LOGS_CHANNEL, f"Пользователю с ID {user_name} изменил уровен на {level} администратор @{message.from_user.username}", message_thread_id=ACTION_THREAD)
                            else:
                                await bot.send_message(BOT_LOGS_CHANNEL, f"Пользователю с ID {user_name} изменил уровен на {level} администратор @{message.from_user.username}")
                        else:
                            return
                    except TelegramAPIError as e:
                        logging.exception(f"Произошла ошибка при отправлении лога: {e}")
            except Exception as e:
                await message.reply(f"Ошибка: {e}")

        async def list_admins(message: types.Message):
            try:
                admins = await execute_query('bot_data.db', "SELECT user_id, username, level FROM admins")

                if admins:
                    # Формируем список администраторов, если таковые имеются
                    admin_list = '\n'.join([f"ID: {admin[0]}, Username: @{admin[1]}, Уровень доступа: {admin[2]}" for admin in admins])
                    response_text = f"Список администраторов:\n{admin_list}"
                else:
                    response_text = 'Список администраторов пуст.'

                await message.reply(response_text)
            except Exception as e:
                await message.reply(f"Ошибка: {e}")
                logging.exception(f"Ошибка в list_admins: {e}")

        async def add_admin(message: types.Message, user_id: int, level: int):
            async with database_lock:
                try:
                    username = (await get_user(user_id))['username']
                    await execute_update('bot_data.db', "INSERT OR IGNORE INTO admins (user_id, username, level) VALUES (?, ?, ?)", (user_id, username, level))
                except Exception as e:
                    await message.reply(f"Ошибка добавления администратора: {e}")

        async def remove_admin(message: types.Message, user_id: int):
            async with database_lock:
                try:
                    success = await execute_update('bot_data.db', "DELETE FROM admins WHERE user_id = ?", (user_id,))
                    if not success:
                        await message.reply(f"Ошибка удаления пользователя из базы данных.")
                except Exception as e:
                    await message.reply(f"Ошибка удаления администратора: {e}")

        async def set_admin_level(message: types.Message, user_id: int, level: int):
            async with database_lock:
                try:
                    await execute_update('bot_data.db', "UPDATE admins SET level = ? WHERE user_id = ?", (level, user_id))
                except Exception as e:
                    await message.reply(f"Ошибка изменения уровня доступа: {e}") 

        dp.message.register(clear_command, Command("clear"))
        
        @dp.message(Command("img"))
        async def img_command(message: types.Message):
            user_id = message.from_user.id
            try:
                img_model = await get_image_model(user_id)
                resolution_options = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text=res, callback_data=f"set_resolution:{res}") for res in list(RESOLUTIONS.keys())[i:i + 2]]
                        for i in range(0, len(RESOLUTIONS), 2)
                    ] + [[InlineKeyboardButton(text=back_txt, callback_data="main_menu")]]
                )
                await message.reply(f"Выберите разрешение для генерации изображения (используется модель {img_model}):", reply_markup=resolution_options)
            except Exception as e:
                logging.exception(f"Ошибка в img_command: {e}")
                await message.reply(f"Произошла ошибка: {e}")
        
        @dp.message(lambda message: isinstance(current_state.get(message.from_user.id), dict) and current_state.get(message.from_user.id).get('state') == 'awaiting_img_query')
        async def handle_img_message(message: types.Message):
            user_id = message.from_user.id
            if current_state.get(user_id, {}).get('state') == 'awaiting_img_query':
                img_query = message.text
                resolution_key = current_state[user_id]['resolution_key']
                previous_generation_params[user_id] = {
                    'img_query': img_query,
                    'resolution_key': resolution_key,
                    'img_model': await get_image_model(user_id)
                }
                image_url = await generate_image(user_id, img_query, resolution_key, bot)

                if image_url:
                    await bot.send_photo(user_id, photo=image_url)
                    await message.reply("Изображение сгенерировано успешно.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="🔄 Повторить генерацию", callback_data=f"repeat_generation:{user_id}")]
                    ]))
                else:
                    await message.reply("Не удалось создать изображение. Попробуйте позже.")
                current_state.pop(user_id, None)  # Clean up the state
                
        @dp.callback_query(lambda query: query.data.startswith("repeat_generation:"))
        async def repeat_generation_callback(query: types.CallbackQuery):
            user_id = int(query.data.split(":")[1])
            params = previous_generation_params.get(user_id)

            if params:
                # Стартуем индикатор "печатает..."
                await start_typing(bot, user_id)
                try:
                    image_url = await try_image_api_providers(params['img_model'], params['img_query'], params['resolution_key'])

                    if image_url:
                        # Отправляем новое сгенерированное изображение
                        await query.message.reply_photo(image_url, caption="Генерация завершена. Хотите повторить?", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="🔄 Повторить генерацию", callback_data=f"repeat_generation:{user_id}")]
                        ]))
                        await query.answer("Изображение сгенерировано снова.")
                    else:
                        await query.answer("Не удалось повторить генерацию изображения. Попробуйте позже.")
                except Exception as e:
                    await query.answer(f"Ошибка: {e}")
                finally:
                    await stop_typing(bot, user_id)
            else:
                await query.answer("Предыдущая генерация не найдена.")
                
        @dp.callback_query(lambda query: query.data.startswith("set_resolution:"))
        async def set_resolution_callback(query: types.CallbackQuery):
            resolution_key = query.data.split(":")[1]
            client_chat_id = query.from_user.id

            try:
                img_model = await get_image_model(client_chat_id)
                query_message = (
                    f"Введите запрос для генерации изображения (модель: {img_model}, разрешение: {resolution_key}):"
                )

                await query.message.edit_text(query_message, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="Отмена", callback_data="main_menu")]
                ]))
                current_state[client_chat_id] = {'state': 'awaiting_img_query', 'resolution_key': resolution_key}
                await query.answer()
            except Exception as e:
                logging.exception(f"Ошибка в set_resolution_callback: {e}")
                await query.answer("Произошла ошибка. Попробуйте позже.")
                          
        @dp.message(IsDocument())
        async def handle_document(message: types.Message):
            file_name = message.document.file_name
            if await is_banned(message.from_user.id):
                return await message.reply("Вы забанены!")

            mime_type = message.document.mime_type
            file_id = message.document.file_id
            file_size = message.document.file_size

            try:
                file = await bot.get_file(file_id)  # Повторный запрос информации о файле
                if file is None:
                    return await message.reply("Ошибка получения информации о файле.")
                # Проверка размера файла
                max_file_size = 6000000  # 6 МБ
                if file_size > max_file_size:
                    return await message.reply(f"Размер файла слишком большой. Максимальный размер: {max_file_size / (1024 * 1024):.2f} MB", parse_mode="Markdown")

                # Check for JSON files FIRST
                if re.match(r"^history.*\.json$", file_name):
                    try:
                        await message.reply("Обработка файла...")
                        file_path = file.file_path
                        file_bytes = await bot.download_file(file_path)
                        file_content_bytes = file_bytes.read()
                        json_data = file_content_bytes.decode('utf-8', errors='ignore')
                        try:
                            json.loads(json_data)  # Check JSON structure
                            if await import_chat_history(message.from_user.id, json_data):
                                await message.reply("Чат успешно загружен!")
                            else:
                                await message.reply("Ошибка импорта истории чата.")
                        except json.JSONDecodeError:
                            await message.reply("Файл не является корректным JSON.")
                    except TelegramAPIError as e:
                        await message.reply(f"Ошибка Telegram API: {e}")
                        logging.exception(e)  # Логируем ошибку для отладки
                    except Exception as e:
                        await message.reply(f"Произошла ошибка: {e}")
                        logging.exception(e)
                    except UnicodeDecodeError:
                        await message.reply("Ошибка декодирования файла. Убедитесь, что файл использует кодировку UTF-8.")
                    except Exception as e:
                        await message.reply(f"Произошла ошибка: {e}")
                #Check for other text files AFTER json check:
                elif mime_type.startswith("text/") or file_name.endswith(('.yml', '.yaml')):
                    file_content = await download_and_decode_file(file_id, bot)
                    if file_content is None:
                        return await message.reply("Не могу обработать файл. Проверьте кодировку и тип файла.", parse_mode="Markdown")
                    truncated_content = file_content[:50000000]  # Ограничение размера текста остается
                    response_text = await generate_response(message.from_user.id, truncated_content, bot)
                else:
                    await message.reply("Пожалуйста, отправьте текстовый файл или JSON файл с именем, начинающимся с 'history'.", parse_mode="Markdown")
            except TelegramAPIError as e:
                await message.reply(f"Ошибка Telegram API: {e}")
            except Exception as e:
                await message.reply(f"Произошла ошибка: {e}")
                logging.exception(e)
                
        @dp.message(F.text == "✨Главное меню") # Используем TextFilter
        async def main_menu_button(message: types.Message):
            await bot.send_message(message.from_user.id, "🏠Главное меню:", reply_markup=main_menu_keyboard)
        
        @dp.message()
        async def handle_all_messages(message: types.Message):
            """Обработчик всех входящих сообщений."""
            user_id = message.from_user.id

            # Создаем очередь для пользователя, если её ещё нет
            if user_id not in user_queues:
                user_queues[user_id] = asyncio.Queue()

            # Проверяем, было ли это первое сообщение от пользователя
            if user_id not in user_first_message:
                user_first_message[user_id] = True
                is_first_message = True
            else:
                is_first_message = False

            # Запускаем задачу обработки очереди, если её ещё нет
            if user_id not in user_tasks:
                task = asyncio.create_task(process_queue(user_id, bot))
                user_tasks[user_id] = task
                if ENGEENER_LOGS:
                    logging.info(f"Запущена задача process_queue для пользователя {user_id}")

            # Добавляем сообщение в очередь
            await user_queues[user_id].put(message)

            # Отправляем немедленное подтверждение, только если это не первое сообщение
            if not is_first_message:
                processing_message = await message.reply("Пожалуйста, подождите, идёт обработка...")
                
                asyncio.create_task(delete_message_after_delay(processing_message.chat.id, processing_message.message_id, 3))

            # Запускаем проверки в отдельных задачах
            is_banned_task = asyncio.create_task(is_banned(user_id))
            is_subscribed_task = asyncio.create_task(check_channel_subscription_cached(user_id, pyrogram_client))

            # Дожидаемся результатов проверок, если нужно, уже после добавления в очередь.
            is_banned_result = await is_banned_task
            if is_banned_result:
                return await message.reply("Вы забанены!")

            is_subscribed_result = await is_subscribed_task
            if not is_subscribed_result:
                await message.answer(f"Для использования бота, подпишитесь на канал {CHANNEL}")
                return

        
        workdir="./pyrogram" # Создайте эту папку вручную
        async with Client(BOT_USERNAME, api_id=API_ID, api_hash=API_HASH, workdir=workdir) as p:
            pyrogram_client = p
            try:
                if not await check_authorization(pyrogram_client):
                    if ENGEENER_LOGS:
                        logging.critical("Авторизация клиента Pyrogram не удалась. Завершение работы.")
                    return

                await bot.get_me()
                try:
                    await dp.start_polling(bot) # Вернулись к стандартному start_polling
                except Exception as e:
                    logging.exception(f"Ошибка во время опроса бота: {e}")
            except sqlite3.OperationalError as e:
                logging.error(f"Ошибка доступа к базе данных Pyrogram: {e}. Попробуйте остановить предыдущий процесс.")
                await shutdown()
            except Exception as e:
                logging.exception(f"Ошибка при работе с Pyrogram: {e}")
                await shutdown()

    except Exception as e:
        logging.critical(f"Необработанная ошибка в main(): {e}")
        traceback.print_exc()
        await shutdown()

    finally:
        await bot.session.close()

async def run_telegram_bot():
    """Функция для запуска Telegram-бота."""
    await main()

def run_flask():
    """Функция для запуска Flask-сервера."""
    asyncio.run(init_db(db_path_responses))  # Инициализация базы данных
    app.run(debug=True, host='0.0.0.0', port=WEB_PORT, use_reloader=False)
    
def main_thread():
    """Основная функция для запуска потоков."""
    # Создаем поток для Flask
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Telegram-бот остается в основном потоке (используете asyncio)
    asyncio.run(run_telegram_bot())

if __name__ == "__main__":
    startup() # Вызываем функцию main()