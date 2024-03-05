import asyncio

from app_agents.roles.ai_novel_video import NovelToVideoAssistant
from app_server import app
from metagpt.logs import logger


async def main():
    with app.app_context():
        msg = "4"
        role = NovelToVideoAssistant()
        logger.info(msg)
        result = await role.run(msg)
        logger.info(result)


asyncio.run(main())
