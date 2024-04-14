import asyncio

from app_agents.roles.ai_novle_video_pro import NovelToVideoAssistantPro
from app_server import app
from metagpt.logs import logger


async def main():
    with app.app_context():
        msg = "4"
        role = NovelToVideoAssistantPro()
        logger.info(msg)
        result = await role.run(msg)
        logger.info(result)


asyncio.run(main())
