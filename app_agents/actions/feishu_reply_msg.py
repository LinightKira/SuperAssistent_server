import asyncio

import config
from feishu_utils.feishu_reply_message import reply_msg_text
from metagpt.actions import Action


class reply_text_msg_to_feishu(Action):
    msg_id: str = ""

    def __init__(self, msg_id: str, *args, **kwargs):
        super().__init__(**kwargs)
        self.msg_id = msg_id

    async def run(self, message: str, *args, **kwargs) -> str:
        res = reply_msg_text(self.msg_id, message)
        if res:
            return res
        else:
            return "error"


async def main():
    msg = "[需求文档](https://uxsxrugqmxi.feishu.cn/file/VVtCb99C5oPRyMxPccUc1ZqDnOb)"

    action = reply_text_msg_to_feishu(msg_id="om_b71795d12557d58298318dd93f1545a2")
    result = await action.run(msg)
    print('res:', result)


if __name__ == '__main__':
    asyncio.run(main())
