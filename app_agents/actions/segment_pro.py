"""
Filename: segment_pro.py
Created Date:2024-02-26 16:46
Author: 宏伟（散人）
"""

import asyncio
from MetaGPT.metagpt.actions import Action
from metagpt.utils.common import OutputParser


# 内容分段
class SegmentPro(Action):
    content: str = ""

    def __init__(self, name: str = "", content: str = "", *args, **kwargs):
        super().__init__(**kwargs)
        self.content = content

    async def run(self, *args, **kwargs) -> list:
        PROMPT = """
        Please convert the novel into a drama script and output it in Json format 
        ## Requirements
        1.Answer strictly in the list format like [{{"narrator": "name","content":"..","screen":".."}}, {{"narrator": "name","content":"..","screen":".."}}]
        2.Pay attention to distinguishing whether the content is dialogue or narration, and the narration narrator is "旁白" ,dialogue narrator is character's name
        3.Each content has less than 20 words.
        4.The screen is picture description of dialogue content, including character actions and background elements,Chinese

        ## Text
        ```{text}```
        """

        prompt = PROMPT.format(text=self.content)
        print('prompt:', prompt)
        resp = await self._aask(prompt=prompt)
        return OutputParser.extract_struct(resp, list)


async def main():
    content = """
这是洛野第一次来派出所。

还是被抓来的。

全程一脸懵逼，洛野在家里打游戏，突然两个警察走了进来，和善的给他戴上了手铐，邀请他坐警车自驾游去派出所。

坐在审讯室，洛野瞪着眼睛，无辜的看着眼前的警察小哥哥。

“姓名。”

“洛野。”

“性别。”

“男。”

“职业。”

“学生。”

“在哪上学？”

“江城大学，明天去报名。”

警察多看了他一眼。

“小伙子长得挺帅，看上去倒也不像会犯错的人。”

警察小哥哥问了一句：“知道自己犯了什么事儿吗？”

洛野连忙摇头。

“不知道？”

警察怀疑的看了他一眼。

“那就解释解释你为什么私闯民宅吧。”

    """
    action = SegmentPro(content=content)
    result = await action.run()
    print('res:', result)


if __name__ == '__main__':
    asyncio.run(main())
