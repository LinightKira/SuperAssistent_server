import asyncio

import config
from feishu_utils.feishu_upload_files import upload_files
from metagpt.actions import Action


class upload_to_feishu(Action):
    parent_node: str = ""

    def __init__(self, parent_node: str, *args, **kwargs):
        super().__init__(**kwargs)
        self.parent_node = parent_node

    async def run(self, file_path, *args, **kwargs) -> str:
        response = upload_files(file_path, self.parent_node)
        if response.code == 0:
            return response.data.file_token
        else:
            print('response code:', response.code)
            print('response msg:', response.msg)
            return 'error'


async def main():
    file_path = 'write_prd.py'
    parent_node = config.Config.FEISHU_ROBOT_UPLOAD_FOLDER_TOKEN

    action = upload_to_feishu(parent_node=parent_node)
    result = await action.run(file_path)
    print('res:', result)


if __name__ == '__main__':
    asyncio.run(main())
