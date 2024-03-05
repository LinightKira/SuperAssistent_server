"""
Filename: get_novel.py
Created Date:
Author: 宏伟（散人）
"""


from MetaGPT.metagpt.actions import Action

from app_server.models.novel import Novel, GetNovelById


class GetNovel(Action):

    def __init__(self, name: str = "", *args, **kwargs):
        super().__init__(**kwargs)

    async def run(self, novel_id: str = '', *args, **kwargs) -> Novel:
        novel = GetNovelById(novel_id)
        print(novel.to_dict())
        print(novel.chapters)
        return novel


