import asyncio
from os import environ

import aiohttp
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

last_news_id_filename = '.data/last_news_id'
last_news_id = 0
with open(last_news_id_filename, 'a+') as fp:
    fp.seek(0)
    fetched_id = fp.read()
    if not fetched_id.isdecimal():
        fp.seek(0)
        fp.truncate()
        fp.write('0')

    else:
        last_news_id = int(fetched_id)


vos_host = 'https://vos.olimpiada.ru'

fetch_news_count = int(environ.get('FETCH_NEWS_COUNT', 50))
update_interval = int(environ.get('UPDATE_INTERVAL', 5 * 60))
channel_id = environ['CHANNEL_ID']

bot = Bot(environ['TOKEN'], default=DefaultBotProperties(parse_mode='html'))
vos_session: aiohttp.ClientSession | None = None


async def update_news():
    global last_news_id

    async with vos_session.get(f'/news/count/{fetch_news_count}') as res:
        page = await res.text()

    web = BeautifulSoup(page, 'lxml')
    news_html = web.find_all(class_='news_headline')
    news_html.reverse()

    for el in news_html:
        news_id = int(el['href'].replace('/news/', ''))
        if news_id <= last_news_id:
            continue

        news_text = el.text

        await bot.send_message(channel_id, f'{news_text}\n'
                                           f'{vos_host}/news/{news_id}')

        last_news_id = news_id
        with open(last_news_id_filename, 'w') as fp:
            fp.write(str(news_id))

        await asyncio.sleep(1)


async def main():
    global vos_session

    vos_session = aiohttp.ClientSession(vos_host)

    while True:
        await update_news()
        await asyncio.sleep(update_interval)


if __name__ == '__main__':
    asyncio.run(main())
