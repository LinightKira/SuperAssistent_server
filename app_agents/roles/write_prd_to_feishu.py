# -*- coding: utf-8 -*-
# @Date    :2024/3/14 15:22
# @Author  : 宏伟（散人）
# @Desc    : 输出产品需求文档，并上传到飞书，完成后发送文件
import asyncio
from datetime import datetime
from pathlib import Path

import config
from app_agents.actions.feishu_reply_msg import reply_text_msg_to_feishu
from app_agents.actions.upload_to_feishu import upload_to_feishu
from app_agents.actions.write_file_name import write_file_name
from app_agents.actions.write_prd import write_prd
from app_server.tools.file_tools import write_file
from metagpt.logs import logger
from metagpt.roles import Role
from metagpt.roles.role import RoleReactMode
from metagpt.schema import Message
from config import Config
from metagpt.utils.file import File


class WritePRDTOFeishu(Role):
    main_title: str = ""
    content: str = ""
    file_path: str = ""
    workspace: str = ""  # 工作区地址
    message_id: str = ""

    def __init__(
            self,
            name: str = "Jobs",
            profile: str = "PRD Master",
            goal: str = "Write PRD to Feishu",
            message_id: str = "",

    ):
        super().__init__()
        self.message_id = message_id
        self.set_actions(
            [write_file_name, write_prd, upload_to_feishu(parent_node=config.Config.FEISHU_ROBOT_UPLOAD_FOLDER_TOKEN),
             reply_text_msg_to_feishu(msg_id=self.message_id)])
        self._set_react_mode(react_mode=RoleReactMode.BY_ORDER.value)
        self.name = name
        self.profile = profile
        self.goal = goal
        self.workspace = Config.WORKSPACE_DIR + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    async def _act(self) -> Message:
        todo = self.rc.todo
        # 写文件名称
        if type(todo) is write_file_name:
            msg = self.get_memories(k=1)[0]  # 找到最相似的 k 条消息
            result = await todo.run(msg.content)
            logger.info(result)
            # 文件名
            self.main_title = result
            return Message(content=result, role=self.profile)
        # 写PRD
        if type(todo) is write_prd:
            msg = self.get_memories(k=1)[0]  # 找到最相似的 k 条消息
            result = await todo.run(msg.content)
            print('write prd:', result)
            logger.info(result)
            # 写入文件
            # self.file_path = await File.write(Path(str(r"%s" % self.workspace)), f"{self.main_title}.md", result.encode('utf-8'))
            self.file_path = await write_file(self.workspace, f"{self.main_title}.md", result.encode('utf-8'))
            print('file_path:', self.file_path)
            if self.file_path is None:
                return Message(content="error", role=self.profile)
            return Message(content=str(result), role=self.profile)
        if type(todo) is upload_to_feishu:
            file_token = await todo.run(self.file_path)
            msg = Message(content=file_token, role=self.profile, cause_by=type(todo))
            self.rc.memory.add(msg)
            return msg
        if type(todo) is reply_text_msg_to_feishu:
            msg = self.get_memories(k=1)[0]  # 找到最相似的 k 条消息
            print('send to feishu msg:', msg.content)
            if msg.content == 'error':
                to_send_message = "出错了，去看日志吧"
            else:
                to_send_message = f"[{self.main_title}](https://uxsxrugqmxi.feishu.cn/file/{msg.content})"
            # result = await todo.run(to_send_message)  # 不需要执行，只需要返回需要回复的信息
            result = to_send_message
            return Message(content=str(result), role=self.profile)

        resp = await todo.run()
        logger.info(resp)
        return Message(content=resp, role=self.profile)


async def start_write_prd_to_feishu(text: str = '', message_id: str = '') -> str:
    print('start write prd:', text)
    role = WritePRDTOFeishu(message_id=message_id)
    result = await role.run(text)
    logger.info(result)
    return result.content


if __name__ == '__main__':
    asyncio.run(start_write_prd_to_feishu("写一个社交APP的产品需求文档", 'om_b71795d12557d58298318dd93f1545a2'))
