import asyncio

from app_agents.actions.get_novel import GetNovel
from app_server import app


async def main():
    with app.app_context():
        n_id = '4'
        action = GetNovel()
        res = await action.run(novel_id=n_id)
        print(res)


if __name__ == '__main__':
    asyncio.run(main())
