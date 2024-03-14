import asyncio

from metagpt.actions import Action


class write_file_name(Action):
    PROMPT_TEMPLATE: str = """
        请帮我提取重要信息，写一个合适的文件名。
        字数越少越好，不要超过10个字
        {content}
        """

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)

    async def run(self, content: str):
        prompt = self.PROMPT_TEMPLATE.format(content=content)

        rsp = await self._aask(prompt)

        return rsp


async def main():
    content = """
    帮我写一个智能聊天机器人的产品需求文档
    """
    action = write_file_name()
    result = await action.run(content)
    print('res:', result)


if __name__ == '__main__':
    asyncio.run(main())
