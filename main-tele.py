import datetime
import requests
import wikipediaapi
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import telegram
from datetime import datetime
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler,  MessageHandler, Filters
import pytz
import random
from telebot import types
import itertools
import json

api_id = "21781680"
api_hash = "e46160ba2fff98eb765d159fa8056162"
YOUR_TOKEN = "5612538430:AAFPa_JE2gPei3K34yGahXG1DUeBQzAUeSI"
OWNER_ID = '@Peercifal'
# OW_api_key = '5e35367c101c25d4b1bef6098febc108'


bot = telegram.Bot(token=YOUR_TOKEN)


def convert_time(strr):
    strr = strr.replace("Z", "")
    a = strr.split(":")
    h = str(int(a[0]) + 1)
    return f"{h}:{a[1]}:{a[2]}"


def convert_data(strr):
    strr = strr.split("-")
    return strr[2] + "/" + strr[1] + "/" + strr[0]


def diffdate(data, f):
    datetime_format = '%d/%m/%Y %H:%M:%S'
    now = datetime.now()
    date1 = data + " " + f
    date2 = now.strftime("%d/%m/%Y %H:%M:%S")
    diff = (datetime.strptime(date1, datetime_format) -
            datetime.strptime(date2, datetime_format))
    return diff


def control_year(year):
    response = requests.get("http://ergast.com/api/f1/{}".format(year))

    if response.status_code == 200:
        return year
    else:
        return "current"


current_year = datetime.now().year

def get_weather(lat, lon):
    try:
        r = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid=5e35367c101c25d4b1bef6098febc108&units=metric"
        )
        if r.status_code == 200:
            weather_data = r.json()
            current_weather = weather_data['weather'][0]['description']
            temperature = weather_data['main']['temp']
            humidity = weather_data['main']['humidity']

            weather_info = f"\n☀️ Погода на трассе:\n"
            weather_info += f"☉ Текущая погода: {current_weather}\n"
            weather_info += f"🌡️ Температура: {temperature}°C\n"
            weather_info += f"💦 Влажность: {humidity}%\n"

            return weather_info
    except ValueError:
        print('Пожалуйста, введите число')


def start(update, context):
    keyboard = [[InlineKeyboardButton("👉НАЧАТЬ👈", callback_data='menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    image_url = 'https://besthqwallpapers.com/ru/download/original/62035'
    caption = f'Добро пожаловать в мир формулы 1! 🏁😊\n\nЯ - твой личный гид по этой увлекательной гоночной серии. Со мной ты всегда будешь в курсе последних результатов и новостей. 📈🏎️\nЯ умею показывать результаты последней гонки и квалификации, а также предоставлять информацию о будущих гонках, пилотах и командах. 💪🌟\nНажми начать и я постараюсь найти для тебя все необходимые сведения о прошлых или будущих заездах.🤔💡\nГотов окунуться в атмосферу быстрой и захватывающей гонки на высочайшем уровне? Тогда приготовься, ведь я собираюсь подарить тебе самую актуальную информацию о формуле 1.🏎️🌍\nПросто нажми начать, и начнем знакомство с миром гран-при! 🚀🔥\n\nДля связи с владельцем нажми {OWNER_ID}'
    bot.send_photo(chat_id=update.effective_chat.id,
                   photo=image_url, caption=caption, reply_markup=reply_markup)


def menu(update, context):
    image_url = 'https://disk.yandex.ru/i/NR-SqHMad6zVIQ'
    keyboard = [
        [InlineKeyboardButton("👨‍🚀 Пилоты", callback_data='drivers'), InlineKeyboardButton(
            "🏎 Конструкторы", callback_data='constructors')],
        [InlineKeyboardButton("🏁 Последняя гонка", callback_data='last_race')],
        [InlineKeyboardButton("🔜 Предстоящая гонка",
                              callback_data='upcoming_races')],
        [InlineKeyboardButton("🕚 Последняя квалификация",
                              callback_data='last_qualifying')],
        [InlineKeyboardButton("🥇 Чемпионы прошлого",
                              callback_data='champion'), InlineKeyboardButton("📰 Новости",
                                                                              callback_data='news')],
        [InlineKeyboardButton("🛣️ Трассы", callback_data='circuits'), InlineKeyboardButton(
            "🎥 Гифка", callback_data='gif')]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    bot.send_photo(chat_id=update.effective_chat.id, photo=image_url)
    context.bot.send_message(chat_id=update.effective_chat.id,
                         text="<b>🤔 О чем ты хочешь узнать👉:</b>", parse_mode='HTML', reply_markup=reply_markup)


def button(update, context):
    query = update.callback_query
    if query.data == '/start':
        start(update, context)
    elif query.data == '/menu':
        menu(update, context)
    elif query.data == 'drivers':
        drivers_info = get_drivers_info()
        query.message.reply_text(drivers_info)
    elif query.data == 'constructors':
        constructors_info = get_constructors_info()
        query.message.reply_text(constructors_info)
    elif query.data == 'last_race':
        last_race_info = get_last_race_info()
        query.message.reply_text(last_race_info)
    elif query.data == 'upcoming_races':
        upcoming_races_info = get_upcoming_race_info()
        query.message.reply_text(upcoming_races_info)
    elif query.data == 'last_qualifying':
        upcoming_races_info = get_qualifying_results()
        query.message.reply_text(upcoming_races_info)
    elif query.data == 'circuits':
        circuits_info = get_circuits_info()
        query.message.reply_text(circuits_info)
    elif query.data == 'gif':
        gif(update, context)
    elif query.data == 'champion':
        send_champion_info(update, context)
    elif query.data == 'news':
        news = get_f1_news()
        for article in news:
            context.bot.send_message(
                chat_id=query.message.chat_id, text=article, parse_mode='HTML')

        keyboard = [
            [InlineKeyboardButton("Еще новость", callback_data='news')],
            [InlineKeyboardButton("Меню", callback_data='menu')]
        ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        context.bot.send_message(chat_id=query.message.chat_id,
                                 text="Выберите действие:", reply_markup=reply_markup)


def get_f1_news():
    api_key = '33ce6ff0cd2240b68c329582a81ba240'
    url = f'https://newsapi.org/v2/everything?q=formula%201&apiKey={api_key}&language=ru'
    response = requests.get(url)
    data = response.json()

    if data['status'] == 'ok':
        articles = data['articles']

        with open('sent_articles.txt', 'r', encoding='utf-8') as file:
            sent_articles = file.read().splitlines()

        for article in articles:
            title = article['title']
            description = article['description']
            url = article['url']

            # Проверяем, была ли статья уже отправлена
            if title not in sent_articles:
                news = f'<a href="{url}">{title}</a>\n\n{description}\n'

                # Добавляем статью в список отправленных статей
                sent_articles.append(title)

                with open('sent_articles.txt', 'a', encoding='utf-8') as file:
                    file.write(title + '\n')

                # Проверяем, требуется ли очистка файла
                if len(sent_articles) >= 10:
                    # Очищаем все строки в файле
                    with open('sent_articles.txt', 'w', encoding='utf-8') as file:
                        file.write('')

                return [news]

    return []


def gif(update, context):

    response = requests.get(
        "https://api.tenor.com/v2/search?q=Formula1&key=AIzaSyAzh3HksxGiFb7jU2xpjBDb_ie-eeBe0cE&limit=20")
    data = response.json()

    if 'results' in data:
        gifs = data['results']
        gif = random.choice(gifs)
        gif_url = gif['media_formats']['mediumgif']['url']
        context.bot.send_message(
            chat_id=update.effective_chat.id, text='Нажмите /menu для вызова меню')
        context.bot.send_animation(
            chat_id=update.effective_chat.id, animation=gif_url)
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="Failed to retrieve GIF.")


def get_drivers_info():
    response = requests.get(
        'http://ergast.com/api/f1/{}/driverStandings.json'.format(current_year))
    standings_data = response.json(
    )['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
    standings_data.sort(key=lambda x: int(x['position']))

    drivers_info = ''
    for i, driver in enumerate(standings_data):
        driver_info = driver['Driver']
        nationality = driver_info['nationality']
        # Функция для получения флага-эмодзи на основе национальности
        flag = get_flag_emoji(nationality)
        drivers_info += f"{i+1}. {flag} {driver_info['givenName']} {driver_info['familyName']} - {driver['points']} очков\n"
    drivers_info += "\n Пилоты рассположены по личному зачету на настоящий момент\n\nВведите номер пилота, чтобы получить подробную информацию (например, '1' для первого пилота) или Нажмите /menu для вызова меню:"
    return drivers_info


def get_flag_emoji(nationality):
    flag_emojis = {
        'British': '🇬🇧',
        'German': '🇩🇪',
        'Spanish': '🇪🇸',
        'Thai': '🇹🇭',
        'Finnish': '🇫🇮',
        'Dutch': '🇳🇱',
        'French': '🇫🇷',
        'Monegasque': '🇲🇨',
        'Danish': '🇩🇰',
        'Mexican': '🇲🇽',
        'Australian': '🇦🇺',
        'American': '🇺🇸',
        'Chinese': '🇨🇳',
        'Canadian': '🇨🇦',
        'Japanese': '🇯🇵',
        'New Zealander': '🇳🇿'# Добавьте больше национальностей и соответствующих флагов-эмодзи
    }
    # Возвращает пустую строку, если национальность не найдена в словаре
    return flag_emojis.get(nationality, '')


def get_driver_details(driver_number):
    response = requests.get(
        'http://ergast.com/api/f1/{}/driverStandings.json'.format(current_year))
    standings_data = response.json(
    )['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
    if driver_number > 0 and driver_number <= len(standings_data):
        driver_info = standings_data[driver_number-1]['Driver']
        driver_details = f"\nПодробная информация о пилоте:\n"
        driver_details += f"👱‍♂️ Имя: {driver_info['givenName']} {driver_info['familyName']}\n"
        driver_details += f"{get_flag_emoji(driver_info['nationality'])} Национальность: {driver_info['nationality']}\n"
        driver_details += f"📅 Дата рождения: {driver_info['dateOfBirth']}\n"
        driver_details += f"#️⃣ Постоянный номер: {driver_info['permanentNumber']}\n"
        # Добавление ссылки на страницу в Википедии
        driver_details += f"Подробнее: {get_driver_wikipedia_link(driver_info)}\n\n"
        return driver_details + "\nНажмите /menu для вызова меню."
    else:
        return "Некорректный номер пилота. Пожалуйста, выберите существующий номер пилота."


def get_driver_wikipedia_link(driver):
    wiki_wiki = wikipediaapi.Wikipedia('mrvoropaev@gmail.com')
    page_py = wiki_wiki.page(f"{driver['givenName']} {driver['familyName']}")
    if page_py.exists():
        return page_py.fullurl
    else:
        return ""


def get_champion_info(year):
    response = requests.get(
        f'http://ergast.com/api/f1/{year}/driverStandings/1.json')
    champion_data = response.json(
    )['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings'][0]

    driver_name = champion_data['Driver']['givenName'] + \
        ' ' + champion_data['Driver']['familyName']
    constructor_name = champion_data['Constructors'][0]['name']

    return driver_name, constructor_name


def send_champion_info(update, context):
    keyboard_champ = []
    years = list(range(1950, 2023))
    rows = list(itertools.zip_longest(*[iter(years)] * 3, fillvalue=None))

    for row in rows:
        buttons = []
        for year in row:
            if year is not None:
                button_text = str(year)
                button_callback = f"champion_{year}"
                button = InlineKeyboardButton(
                    text=button_text, callback_data=button_callback)
                buttons.append(button)
        keyboard_champ.append(buttons)

    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard_champ)

    if update.message is not None:
        chat_id = update.message.chat.id
    else:
        chat_id = update.effective_chat.id

    context.bot.send_message(chat_id, "Выберите год:",
                             reply_markup=reply_markup)


def handle_champion_query(update, context):
    year = update.callback_query.data.split('_')[1]
    champion_info = get_champion_info(year)
    champion_info_str = ", ".join(champion_info)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=champion_info_str + "\nНажмите /menu для вызова меню.")


def handle_message(update, context):
    if update.message.text == '/menu':
        menu(update, context)  # вызов функции menu
        return

    try:
        driver_number = int(update.message.text)
        driver_details = get_driver_details(driver_number)
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=driver_details)
    except ValueError:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text='Пожалуйста, введите число')


def get_constructors_info():
    response = requests.get(
        'http://ergast.com/api/f1/{}/constructorStandings.json'.format(current_year))
    standings_data = response.json(
    )['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']
    constructors_data = []

    for standing in standings_data:
        constructor_data = standing['Constructor']
        constructors_data.append(constructor_data)

    constructors_info = []

    for constructor in constructors_data:
        info = {
            "Название": constructor['name'],
            "Подробно": constructor['url'],
            "Национальность": constructor['nationality']
        }
        constructors_info.append(info)

    output = ""
    for info in constructors_info:
        output += f"Название: {info['Название']}\n"
        output += f"Подробно: {info['Подробно']}\n"
        output += f"Национальность: {info['Национальность']}\n\n"

    return output + "\nКоманды рассположены по месту в зачете в кубке конструкторов на настоящий момент\n\nНажмите /menu для вызова меню."

# Добавим обработку ошибки IndexError


def get_constructor_info(constructor_name):
    try:
        response = requests.get(
            'http://ergast.com/api/f1/{}/constructors.json'.format(current_year))
        constructors_data = response.json(
        )['MRData']['ConstructorTable']['Constructors']

        for constructor_data in constructors_data:
            if constructor_data['name'] == constructor_name:
                return constructor_data
        return None
    except IndexError:
        print("Ошибка: индекс списка выходит за пределы диапазона")
        return None


def get_last_race_info():
    race_data = None
    try:
        response = requests.get(
            'http://ergast.com/api/f1/current/last/results.json')

        if response.status_code == 200:
            race_data = response.json()['MRData']['RaceTable']['Races'][0]
            last_race_name = race_data['raceName']
            race_info = f"Последняя гонка:\n"
            race_info += f"Название: {race_data['raceName']}\n"
            race_info += f"Дата: {race_data['date']}\n"
            race_info += f"Кругов: {race_data.get('laps', 'Информация недоступна')}\n"
            race_info += f"Дистанция: {race_data.get('distance', 'Информация недоступна')}\n"

            # Добавление ссылки на Википедию
            wiki_link = race_data.get('url', '')
            if wiki_link:
                race_info += f"Ссылка на Википедию: {wiki_link}\n"

            # Добавление новостей о последней гонке Формулы 1
            race_info += get_last_race_news(last_race_name)

            # Добавление результатов гонки по пилотам
            race_info += get_race_results()

            return race_info + "\nНажмите /menu для вызова меню."
        else:
            return "Информация недоступна"
    except requests.exceptions.RequestException as e:
        print("Ошибка при запросе данных:", str(e))

    return race_data


def get_race_results():
    race_results_data = None
    try:
        response = requests.get(
            'http://ergast.com/api/f1/current/last/results.json')

        if response.status_code == 200:
            race_results_data = response.json(
            )['MRData']['RaceTable']['Races'][0]
            race_results_info = "\nРезультаты гонки (позиция, имя, время, очки):\n"
            winner_info = race_results_data['Results'][0]
            winner_name = winner_info['Driver']['givenName'] + \
                ' ' + winner_info['Driver']['familyName']
            winner_time = winner_info.get('Time', {}).get('time', 'N/A')
            nationality = winner_info['Driver']['nationality']
            flag = get_flag_emoji(nationality)
            points = winner_info['points']
            race_results_info += f"🏆 {flag} {winner_name} - {winner_time} ({points})\n"
            # race_results_info += f"Очки: {points}\n\n"

            for i, result in enumerate(race_results_data['Results'][1:], start=2):
                driver_name = result['Driver']['givenName'] + \
                    ' ' + result['Driver']['familyName']
                time_difference = result.get('Time', {}).get('time', 'N/A')
                nationality = result['Driver']['nationality']
                flag = get_flag_emoji(nationality)
                points = result['points']
                race_results_info += f"{i}. {flag} {driver_name} - {time_difference} ({points})\n"

            return race_results_info
        else:
            return "Информация недоступна"
    except requests.exceptions.RequestException as e:
        print("Ошибка при запросе данных:", str(e))

    return race_results_data


def get_last_race_news(last_race_name, num_articles=3):
    api_key = '33ce6ff0cd2240b68c329582a81ba240'
    last_race_name = last_race_name.replace(' ', '%20')
    newsapi_link = f"https://newsapi.org/v2/everything?q={last_race_name}&apiKey={api_key}&language=ru"

    response = requests.get(newsapi_link)

    if response.status_code == 200:
        news = response.json()
        articles = news['articles']
        news_info = "\nНовости о последней гонке Формулы 1 👉\n"

        for i, article in enumerate(articles[:num_articles]):
            title = article['title']
            url = article['url']
            news_info += f"Заголовок: {title}\n"
            news_info += f"Ссылка: {url}\n\n"

        return news_info
    else:
        print('Ошибка при получении новостей')
        return ""


def get_qualifying_results():
    qualifying_data = None
    try:
        response = requests.get(
            'http://ergast.com/api/f1/current/last/qualifying.json')

        if response.status_code == 200:
            qualifying_data = response.json(
            )['MRData']['RaceTable']['Races'][0]
            qualifying_info = "\nРезультаты квалификации:\n\n"

            for result in qualifying_data['QualifyingResults']:
                driver_name = result['Driver']['givenName'] + \
                    ' ' + result['Driver']['familyName']
                position = result['position']
                nationality = result['Driver']['nationality']
                flag = get_flag_emoji(nationality)
                q1_time = result['Q1']
                q2_time = result.get('Q2', 'N/A')
                # Используя метод get(), если ключ 'Q3' не существует в словаре result, он вернет значение по умолчанию 'N/A' вместо возникновения KeyError
                q3_time = result.get('Q3', 'N/A')
                qualifying_info += f"{position}. {flag} {driver_name} \n"
                qualifying_info += f"Q1: {q1_time}\n"
                qualifying_info += f"Q2: {q2_time}\n"
                qualifying_info += f"Q3: {q3_time}\n\n"

            return qualifying_info + "\nНажмите /menu для вызова меню."
        else:
            return "Информация недоступна"
    except requests.exceptions.RequestException as e:
        print("Ошибка при запросе данных:", str(e))

    return qualifying_data


def get_circuits_info():
    response = requests.get('http://ergast.com/api/f1/2023/circuits.json')
    circuits_data = response.json()['MRData']['CircuitTable']['Circuits']

    circuits_info = ""
    for circuit_data in circuits_data:
        circuit_name = circuit_data['circuitName']
        circuit_location = circuit_data['Location']['locality'] + \
            ', ' + circuit_data['Location']['country']

        country = circuit_data['Location']['country']
        flag_country = get_flag_emoji_country(country)
        circuits_info += f"🏁 Название: {circuit_name}\n"
        circuits_info += f"🖈 Местоположение: {circuit_location}{flag_country}\n"
        circuits_info += f"❓ Подробнее: {get_circuit_wikipedia_link(circuit_name)}\n\n"

    return circuits_info + "\nНажмите /menu для вызова меню."


def get_circuit_wikipedia_link(circuit_name):
    wiki_wiki = wikipediaapi.Wikipedia('mrvoropaev@gmail.com')
    page_py = wiki_wiki.page(circuit_name)
    if page_py.exists():
        return page_py.fullurl
    else:
        return ""


def get_upcoming_race_info():
    ergast_link = "https://ergast.com/api/f1/current/next.json"

    response = requests.get(ergast_link)

    if response.status_code == 200:
        race_info = response.json()
        race_data = race_info['MRData']['RaceTable']['Races'][0]
        race_name = race_data['raceName']
        race_location = race_data['Circuit']['Location']
        circuit_name = race_data['Circuit']['circuitName']
        country = race_data['Circuit']['Location']['country']
        date = race_data['date']
        time = race_data['time']

        # Convert time to local time
        utc_time = datetime.strptime(date + " " + time, "%Y-%m-%d %H:%M:%SZ")
        # Replace 'Europe/Moscow' with your desired timezone
        local_timezone = pytz.timezone('Europe/Moscow')
        local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(
            local_timezone).strftime('%H:%M')

        flag_country = get_flag_emoji_country(country)
        upcoming_race_info = f"\n🏎 Информация о следующей гонке Формулы1: \n"
        upcoming_race_info += f"🔄 Название гонки: {race_name}  \n"
        upcoming_race_info += f"🛣 Трасса: {circuit_name} \n"
        upcoming_race_info += f"{flag_country} Страна: {country}\n"
        upcoming_race_info += f"📅 Дата: {date} \n"
        upcoming_race_info += f"⏳ Время начала (в вашем регионе):  {local_time}\n"

        # Get weather information for the race location
        lat = race_location['lat']
        lon = race_location['long']
        # OW_api_key = "5e35367c101c25d4b1bef6098febc108"
        weather_info = get_weather(lat, lon)
        upcoming_race_info += weather_info

        stream_link = check_live_stream()
        if stream_link:
            telegram_link = stream_link
            upcoming_race_info += f"🎥 Ссылка на трансляцию: {telegram_link}\n"


        return upcoming_race_info + "\nНажмите /menu для вызова меню."
    else:
        print('Ошибка при получении информации о следующей гонке')
        return ""

def get_flag_emoji_country(country):
    flag_emojis_country = {
        'Australia': '🇦🇺',
        'USA': '🇺🇸',
        'Bahrain': '🇧🇭',
        'Azerbaijan': '🇦🇿',
        'Netherlands': '🇳🇱',
        'Spain': '🇪🇸',
        'Hungary': '🇭🇺',
        'Brazil': '🇧🇷',
        'Singapore': '🇸🇬',
        'Monaco': '🇲🇨',
        'Italy': '🇮🇹',
        'Austria': '🇦🇹',
        'France': '🇫🇷',
        'Mexico': '🇲🇽',
        'UK': '🇬🇧',
        'Belgium': '🇧🇪',
        'Japan': '🇯🇵',
        'Canada': '🇨🇦',
        'UAE': '🇦🇪',
        'Saudi Arabia': '🇸🇦',
        'New Zealand': '🇳🇿'
        # Добавьте больше национальностей и соответствующих флагов-эмодзи
    }
    # Возвращает пустую строку, если национальность не найдена в словаре
    return flag_emojis_country.get(country, '')

def check_live_stream():
    channel_username = 'stanizlavsky'
    channel = bot.get_chat('@' + channel_username)

    updates = bot.get_updates()
    for update in updates:
        message = update.effective_message
        if message.chat.id == channel.id and message.live_period and message.live_period > 0:
            return 'https://t.me/' + channel_username

    return False


def main():
    updater = Updater(bot=bot, use_context=True)
    dp = updater.dispatcher
    # message_handler = MessageHandler(Filters.text, handle_message)
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(menu, pattern='^menu$'))
    dp.add_handler(CallbackQueryHandler(
        handle_champion_query, pattern='^champion_'))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.text, handle_message))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()