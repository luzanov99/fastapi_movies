import logging
import  uvicorn as uvicorn
import core.config as config
from typing import Union
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from core.logger import LOGGING
from db import redis
from db import elastic
from elasticsearch import AsyncElasticsearch
import aioredis
app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)
@app.on_event('startup')
async def startup():
    redis.redis = await aioredis.create_redis_pool((config.REDIS_HOST, config.REDIS_PORT), minsize=10,maxsize=20)
    elastic.es = AsyncElasticsearch(hosts=[f'{config.ELASTIC_HOST}: {config.ELASTIC_PORT}'])

@app.on_event('shutdown')
async def shutdown():
    await redis.redis.close()
    await elastic.es.close()


@app.get('/items/{item_id}/')
def read_items(item_id: int, q: Union[str,None]=None):
    return {"item_id":item_id, "q":q}


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )