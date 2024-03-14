import asyncio

from metagpt.actions import Action


class write_prd(Action):
    PROMPT_TEMPLATE: str = """
        你是产品专家，
        我的需求是：{theme}
        请使用Markdown格式写出产品需求文档。
        """

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)

    async def run(self, content: str):
        prompt = self.PROMPT_TEMPLATE.format(theme=content)

        rsp = await self._aask(prompt)

        return rsp


async def main():
    content = """
    帮我写一个智能聊天机器人的产品需求文档
    """
    action = write_prd()
    result = await action.run(content)
    print('res:', result)


if __name__ == '__main__':
    asyncio.run(main())
