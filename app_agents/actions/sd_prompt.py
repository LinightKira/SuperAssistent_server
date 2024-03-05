"""
Filename: sd_prompt.py
Created Date:
Author: 宏伟（散人）
"""

import asyncio
import re

from MetaGPT.metagpt.actions import Action
from app_agents.models.novel_character import NovelCharacter
from app_agents.utils.textTools import replace_newlines


class MakeSDPrompt(Action):
    content: str = ""
    character: NovelCharacter = None

    def __init__(self, name: str = "", content: str = "", character: NovelCharacter = None, *args, **kwargs):
        super().__init__(**kwargs)
        self.content = content
        self.character = character

    async def run(self, *args, **kwargs) -> str:
        PROMPT = """
                   Please extract the keywords from this article and supplement them with visual descriptions, and divide them into English words.
                   1.If there are characters, use 1girl or 1boy or Ngirls or Nboys to start.(N is the number of characters)
                   2.You need to describe the details in the picture as much as possible, including expression, actions, clothing, posture, background, environment,etc
                   3.The output must be strictly in the specified language, English.
                   4.Words must be separated by a comma.
                   5.The content you output can only contain words that describe the image
                   The text delimited by triple backticks.
                   ```{content}```
                   """
        prompt = PROMPT.format(content=self.content)

        resp = await self._aask(prompt=prompt)
        resp = replace_newlines(resp)  # 去除换行

        if self.character:
            resp = self.add_character_prompts(resp)
        return resp

    def add_character_prompts(self, prompts):
        pattern = r'1(boy|girl)'
        if re.search(pattern, prompts):
            # 如果匹配到,则替换为当前角色的描述
            return re.sub(pattern, self.character.sd_prompts, prompts)
        else:
            return self.character.sd_prompts + ',' + prompts


async def main():
    content = """
    这是我第一次来到派出所，被误会了。
    """

    character = NovelCharacter(name='拉克丝', gender='女',
                               sd_prompts='lacus clyne, blue eyes, hair ornament, long hair, wave hair ornament, pink hair')
    action = MakeSDPrompt(content=content, character=character)
    result = await action.run()
    print('res:', result)


if __name__ == '__main__':
    asyncio.run(main())
