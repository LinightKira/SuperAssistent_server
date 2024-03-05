# -*- coding: utf-8 -*-
# @Date    :
# @Author  : 宏伟（散人）
# @Desc    :
import os
import re
from datetime import datetime
from itertools import cycle

from app_agents.actions.design_roles import DesignNovelRoles
from app_agents.actions.get_novel import GetNovel
from app_agents.actions.make_video import MakeVideo
from app_agents.actions.sd_prompt import MakeSDPrompt
from app_agents.actions.sd_text_to_image import SD_t2i
from app_agents.actions.segment_pro import SegmentPro
from app_agents.actions.tts_edge import EdgeTTS
from app_agents.models.novel_character import NovelCharacter
from app_agents.utils.fileTools import create_AINovelVideoDir
from metagpt.actions import Action
from metagpt.logs import logger
from metagpt.provider.human_provider import HumanProvider
from metagpt.roles import Role
from metagpt.schema import Message
from config import Config


class TextToVideoAssistantPro(Role):
    context: str = ""
    workspace: str = ""  # 工作区地址
    characters: list[NovelCharacter] = []  # 角色信息
    total_storyboard: int = 0  # 总段落数
    current_storyboard_number: int = 0  # 正在处理的段落编号

    def __init__(
            self,
            name: str = "hong",
            profile: str = "TextToVideoPro Assistant",
            goal: str = "Generate text videos",
            context: str = "",

    ):
        super().__init__()
        self.context = context
        self.set_actions([DesignNovelRoles(content=context), SegmentPro(content=context)])
        self.name = name
        self.profile = profile
        self.goal = goal
        self.workspace = Config.WORKSPACE_DIR + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        # 创建工作目录
        create_AINovelVideoDir(self.workspace)

    async def _think(self) -> None:
        """Determine the next action to be taken by the role."""
        logger.info(self.rc.state)
        if self.rc.todo is None:
            self._set_state(0)
            return

        if self.rc.state + 1 < len(self.states):

            self._set_state(self.rc.state + 1)
        else:

            self.rc.todo = None

    async def _react(self) -> Message:
        msg = None
        while True:
            await self._think()
            if self.rc.todo is None:
                break
            msg = await self.act()
        return msg

    async def act(self) -> Message:
        todo = self.rc.todo

        # 设计角色
        if type(todo) is DesignNovelRoles:
            resp = await todo.run()
            logger.info(resp)
            # 更新角色信息、配音
            self.update_characters(resp)
            # 打印角色
            self.print_characters()
            return Message(content=str(resp), role=self.profile)

        # 分镜处理
        if type(todo) is SegmentPro:
            resp = await todo.run()
            logger.info(resp)
            print('segment resp:', resp)
            actions = list()
            # 获取总段落数
            self.total_storyboard = len(resp)
            # 生成图片和语音
            for i, v in enumerate(resp):
                print('segment_', i, ':====', v)
                narrator = v.get('narrator')
                if not narrator:
                    narrator = "旁白"
                content = v.get('content')
                if not content:
                    content = v.get('screen')
                screen = v.get('screen')
                if not screen:
                    screen = v.get('content')

                # 1、生成sd 文生图提示词
                character = self.get_character_in_screen(screen)
                if character:
                    actions.append(MakeSDPrompt(content=screen, character=character))
                else:
                    # 没有角色则使用默认参数
                    actions.append(MakeSDPrompt(content=screen))

                # 2、生成TTS语音片段
                tts_path = self.workspace + "/tts/" + datetime.now().strftime(
                    "%Y-%m-%d_%H-%M-%S") + '_' + str(
                    i) + ".mp3"

                # 旁白使用默认角色
                if narrator == "旁白":
                    actions.append(EdgeTTS(content=content, output=tts_path))
                else:
                    voice = self.get_voice(narrator)
                    if voice:
                        actions.append(EdgeTTS(content=content, voice=voice, output=tts_path))
                    else:
                        # 没有找到配音使用默认
                        actions.append(EdgeTTS(content=content, output=tts_path))
            self._add_actions(actions)

            return Message(content=str(resp), role=self.profile)

        # SD提示词处理
        if type(todo) is MakeSDPrompt:
            resp = await todo.run()
            logger.info(resp)
            # 调用文生图Act
            # print('即将调用文生图，提示词如下：', resp)
            images_path = self.workspace + "/image"
            act = SD_t2i(prompts=resp, save_path=images_path)
            self._add_actions([act])
            return Message(content=resp, role=self.profile)

        if type(todo) is EdgeTTS:
            resp = await todo.run()
            # 动态更新分镜标志位
            logger.info(resp)
            return Message(content=resp, role=self.profile)

        if type(todo) is SD_t2i:
            resp = await todo.run()
            # 判断当前章节是否合成完毕，如果合成完毕，则进行视频合成
            self.current_storyboard_number += 1
            logger.info(resp)
            if self.current_storyboard_number == self.total_storyboard:

                act = MakeVideo(workspace=self.workspace)
                self._add_actions([act])

            return Message(content=resp, role=self.profile)
        resp = await todo.run()
        logger.info(resp)
        return Message(content=resp, role=self.profile)

    def _add_actions(self, actions):
        start_idx = len(self.actions)
        for idx, action in enumerate(actions):
            if not isinstance(action, Action):
                # 默认初始化
                i = action(name="", llm=self.llm)
            else:
                if self.is_human and not isinstance(action.llm, HumanProvider):
                    logger.warning(
                        f"is_human attribute does not take effect, "
                        f"as Role's {str(action)} was initialized using LLM, "
                        f"try passing in Action classes instead of initialized instances"
                    )
                i = action
            self._init_action(i)
            self.actions.append(i)
            self.states.append(f"{idx + start_idx}. {action}")

    # 动态更新章节分镜

    # 更新角色信息
    def update_characters(self, char_data):
        male_voices = cycle([v for v in Config.VOICES if Config.VOICES[v] == 'Male'])
        female_voices = cycle([v for v in Config.VOICES if Config.VOICES[v] == 'Female'])

        for name, desc in char_data.items():

            gender = desc.split(',')[0]
            # 使用正则表达式替换male/female
            pattern = r'\b(male|Male|female|Female)\b'
            sd_prompts = re.sub(pattern, lambda x: '1boy' if x.group(1).lower() == 'male' else '1girl', desc)

            existed = False
            for c in self.characters:
                if c.name == name:
                    c.sd_prompts = sd_prompts
                    existed = True
                    break

            if not existed:
                if gender == 'male':
                    voice = next(male_voices)
                else:
                    voice = next(female_voices)

                while voice in [c.voice for c in self.characters]:
                    # 检查所有已存在角色
                    voice = next(male_voices) if gender == 'male' else next(female_voices)
                c = NovelCharacter(name, gender, sd_prompts, voice=voice)
                self.characters.append(c)

    def print_characters(self):
        print('所有角色:')
        for c in self.characters:
            print(f'- 名字:{c.name}')
            print(f'- 性别:{c.gender}')
            print(f'- 描述:{c.sd_prompts}')
            print(f'- 配音:{c.voice}')
            print()

    # 获取角色配音
    def get_voice(self, narrator):
        for c in self.characters:
            if c.name == narrator:
                return c.voice
        return None

    # 获取分镜画面中的角色
    def get_character_in_screen(self, screen):
        for c in self.characters:
            if c.name in screen:
                return c
        return None


async def start_ai_text_video_pro(text: str = ''):
    print('start TextToVideoAssistantPro:', text)
    msg = text
    role = TextToVideoAssistantPro()
    logger.info(msg)
    result = await role.run()
    logger.info(result)
