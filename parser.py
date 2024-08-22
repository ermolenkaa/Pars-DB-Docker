import re
import aiohttp
import asyncio
from datetime import datetime, timedelta, timezone
from database import engine, Base
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import SessionLocal, engine
from models import News
import logging
from bs4 import BeautifulSoup



logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def clean_text(text):
    # Удаление HTML-тегов
    soup = BeautifulSoup(text, 'html.parser')
    clean_text = soup.get_text()

    # Удаление лишних пробелов и символов новой строки
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()

    return clean_text

"""async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized")"""

async def fetch_news():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://russian.rt.com/rss') as response:
                content = await response.text()
                return content
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        return None

async def parse_rss(content):
    try:
        soup = BeautifulSoup(content, 'lxml-xml')
        news_items = []

        for item in soup.find_all('item'):
            title = item.find('title').text
            link = item.find('link').text
            published = item.find('pubDate').text
            description = item.find('description').text
            published_dt = datetime.strptime(published, '%a, %d %b %Y %H:%M:%S %z')

            now = datetime.now(timezone.utc)
            if published_dt >= now - timedelta(hours=1):
                published_date = published_dt.date()
                published_time = published_dt.time()
                clean_description = await clean_text(description)
                news_items.append({
                    'title': title,
                    'url': link,
                    'text': clean_description,
                    'date': published_date,
                    'time': published_time
                })

        return news_items
    except Exception as e:
        logger.error(f"Error parsing RSS: {e}")
        return []

async def save_news(news_data):
    try:
        async with SessionLocal() as session:
            for news in news_data:
                existing_news = await session.execute(select(News).where(News.url == news['url']))
                if not existing_news.scalars().first():
                    new_news = News(
                        title=news['title'],
                        text=news['text'],
                        url=news['url'],
                        date=news['date'],
                        time=news['time'].strftime('%H:%M:%S')  # Convert time to string
                    )
                    session.add(new_news)
            await session.commit()
            logger.info("News data saved successfully")
    except Exception as e:
        logger.error(f"Error saving news: {e}")


async def main():
   # await init_db()
    while True:
        content = await fetch_news()
        if content:
            news_data = await parse_rss(content)
            if news_data:
                await save_news(news_data)
                logger.info("Fetched and saved news data")
            else:
                logger.info("No news data found")
        await asyncio.sleep(600)  # 10 minutes

if __name__ == "__main__":
    asyncio.run(main())
