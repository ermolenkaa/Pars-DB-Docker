from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import SessionLocal, engine
from models import News
import logging
from pydantic import BaseModel
from typing import Optional, Any

app = FastAPI()

logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)
logging.info('Start logging')

async def get_db():
    async with SessionLocal() as session:
        yield session

class DefaultResponse(BaseModel):
    """Стандартный ответ от API."""
    error: bool
    message: Optional[str]
    payload: Optional[list]

@app.get("/news", response_model=DefaultResponse)
async def get_news(limit: int = 10, offset: int = 0, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(News).offset(offset).limit(limit))
        news = result.scalars().all()
        response = []
        for news_item in news:
            id = news_item.id
            date = news_item.date
            time = news_item.time
            title = news_item.title
            text = news_item.text
            url = news_item.url
            dict_item = {
                "id": id,
                "date": date,
                "time": time,
                "title": title,
                "text": text,
                "url": url
            }
            response.append(dict_item)
        return DefaultResponse(error=False, message="Ok", payload=response)
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        return DefaultResponse(error=True, message="Error fetching news", payload=None)

@app.get("/news/{news_id}", response_model=DefaultResponse)
async def get_news_by_id(news_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(News).where(News.id == news_id))
        news = result.scalars().first()
        id = news.id
        date = news.date
        time = news.time
        title = news.title
        text = news.text
        url = news.url
        dict_item = {
            "id": id,
            "date": date,
            "time": time,
            "title": title,
            "text": text,
            "url": url
        }
        return DefaultResponse(error=False, message="Ok", payload=[dict_item])
    except Exception as e:
        logger.error(f"Error fetching news by ID: {e}")
        return DefaultResponse(error=True, message="Error fetching news by ID", payload=None)

@app.delete("/news/{news_id}", response_model=DefaultResponse)
async def delete_news(news_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(News).where(News.id == news_id))
        news = result.scalars().first()
        await db.delete(news)
        await db.commit()
        return DefaultResponse(error=False, message="News deleted", payload=[{"id": news_id}])
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error deleting news: {e}")
        return DefaultResponse(error=True, message="Error deleting news", payload=None)
