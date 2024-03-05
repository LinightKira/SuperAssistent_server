"""
Filename: design_roles.py
Created Date:
Author: 宏伟（散人）
"""

import asyncio

import config
from app_agents.utils.textTools import novel_filter_text
from metagpt.actions import Action
from metagpt.actions.action_node import ActionNode
from metagpt.utils.common import OutputParser


# prompt备份
# 2.The character must have full name.Pay attention to the correspondence between nicknames and full names

GET_ROLES_NODE = ActionNode(
    key="Get Roles Node",
    expected_type=dict,
    instruction="""
            1.Extract characters with names from the context and label them with gender.
            2.The output must be strictly in the specified language, Chinese.
            3.Output in dictionary format, such as {"张三": "男", "李四": "女"}
            """,
    example="{\"张三\": \"男\", \"李四\": \"女\"}"
)

DESIGN_ROLES_NODE = ActionNode(
    key="Design Roles Node",
    expected_type=dict,
    instruction="""
        1. Please help me add character descriptions for each of the above characters, including gender, facial shape, hair color, and clothing
        2. Output in dictionary format, such as {"张三", "male, blue eyes,..."}
        3. The name must be in Chinese, and the description section must be in English words
        """,
    example="{\"张三\": \"male, oval_face, chestnut_brown_hair, slim_body, elegant_formal_wear\", \"李四\": \"female, heart-shaped_face, dark_brown_hair, graceful_slender_body, stylish_elegant_fashion\"}"
)

## 选声音没搞定
VOICE_LIST = config.Config.VOICES
SELECT_VOICE_PROMPT = """ 
        1. Please help me choose a spokesperson based on the gender of the character
        2. Output in list format such as [{\"name\": \"小明\",\"sd_prompts\": \"male, oval_face, chestnut_brown_hair, slim_body,...\",\"voice\": \"zh-CN-xxx\"},{\"name\": \"小红\",\"sd_prompts\": \"female, heart-shaped_face, dark_brown_hair,graceful_slender_body,...\",\"voice\": \"zh-CN-xxx\"}"
        3. The speaker must choose from the following sounds
        ## Voices List"""
SELECT_VOICE_INSTRUCTION = f"{SELECT_VOICE_PROMPT}\n{VOICE_LIST}"

SELECT_CHARACTER_VOICE_NODE = ActionNode(
    key="Select character voice",
    expected_type=list,
    instruction=SELECT_VOICE_INSTRUCTION,
    example="[{\"name\": \"小明\",\"sd_prompts\": \"male, oval_face, chestnut_brown_hair, slim_body,...\",\"voice\": "
            "\"zh-CN-xxx\"},{\"name\": \"小红\",\"sd_prompts\": \"female, heart-shaped_face, dark_brown_hair,"
            "graceful_slender_body,...\",\"voice\": \"zh-CN-xxx\"}"
)


class Designer_NODES(ActionNode):
    def __init__(self, name="Designer Nodes", expected_type=str, instruction="", example=""):
        super().__init__(key=name, expected_type=str, instruction=instruction, example=example)
        self.add_children([GET_ROLES_NODE, DESIGN_ROLES_NODE])

    async def fill(self, context, llm, schema="raw", mode="auto", strgy="complex"):
        self.set_llm(llm)
        self.set_context(context)
        # print('Designer nodes fill')
        # print('context:')  # 提示词 结构化后的prompts
        # print(context)
        # print('==================')
        if self.schema:
            schema = self.schema

        if strgy == "simple":
            return await self.simple_fill(schema=schema, mode=mode)
        elif strgy == "complex":  # 复杂模式
            # 这里隐式假设了拥有children
            child_context = context  # 输入context作为第一个子节点的context
            for _, i in self.children.items():
                i.set_context(child_context)  # 为子节点设置context
                # print('child context')
                # print(child_context)
                # print('====================')
                child = await i.simple_fill(schema=schema, mode=mode)
                # print('child：')
                # print(child.content)
                # print('====================')
                child_context = child.content  # 将返回内容（child.content）作为下一个子节点的context

            self.content = child_context  # 最后一个子节点返回的内容设置为父节点返回内容（self.content）
            # print('Designer nodes return content')
            # print(self.content)
            # print('====================')
            return self


class DesignNovelRoles(Action):
    content: str = ""
    characters: list = []

    def __init__(self, name: str = "", content: str = '', characters: list = '', *args, **kwargs):
        super().__init__(**kwargs)
        self.content = novel_filter_text(content)
        self.characters = characters
        self.node = Designer_NODES()

    async def run(self, *args, **kwargs) -> dict:
        #  PROMPT = """
        #  ## text
        #  {content}
        #  -----
        #
        #  ## format example
        # {{"张三": "男", "李四": "女"}}
        # ## nodes:
        #  Extract characters with names from the text and label them with gender.
        #  The character must have full name.
        #  ## constraint
        #  The output must be strictly in the specified language, Chinese.
        #  ## action
        #  Follow instructions of nodes, generate output and make sure it follows the format example.
        #  """

        # resp = await self._aask(prompt=prompt)

        if self.characters:
            print('characters', self.characters)

        PROMPT = """
        {content}
        """
        prompt = PROMPT.format(content=self.content)

        rsp_node = await self.node.fill(context=prompt, llm=self.llm, schema="raw",
                                        strgy="complex")  # 运行子节点，获取返回（返回格式为ActionNode）（注意设置 schema="raw" ）
        resp = rsp_node.content  # 获取返回的文本内容

        print('design action run:', resp)

        return OutputParser.extract_struct(resp, dict)


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

警察小哥哥怀疑洛野是见色起意。

没办法，警察小哥哥⻅到那家的主人后，也只能想到这个理由。

毕竟那小姑娘太美了。

“啥私闯⺠宅？”

洛野满脸疑惑，看着洛野天真的眼神，也不像是在作假，警察小哥哥也迷茫了：“你为什么会出现在教师公寓五栋四单元614？”

“614？那我家啊。”

警察小哥哥拿出手中的资料，看了一眼后怒道：“小伙子，这是警察局，坦白从宽，抗拒从严。”

“老实交代，你为什么在614。”

“......那真是我家。”

洛野急了，为什么说实话没人信呢。

难道他美好的大学生活还没开始，就要蹲局子了吗？

“614的业主是江城大学的一位教授，这位教授将房间租给了一个学生，这个学生是女的，不是你。”

“租？教授？”

洛野的面色逐渐明朗：“那位教授是不是叫顾明轩？”

“呦呵，调查的还挺仔细。”

洛野：“……”

“顾明轩是我哥。”

警察一愣，又看了看资料。

“我再说一遍，这里是警察局，你姓洛，他姓顾，编瞎话编到警察局来了？”

洛野寻思了一下，这个时间顾明轩应该在⻜机上，手机关机，所以警察联系不到他。

洛野是江城大学的新生，为什么要考江城大学呢？

因为他高中暗恋了三年的女神答应他，只要他能考上江城大学，就跟他在一起。

其次，因为他哥顾明轩是江大的教授，他来江大干啥都方便。

但是没想到他哥把他扔在江大后，就坐⻜机出国攻读第四个博士学位去了。

距离开学还有一天，所以他就去了学校分配给他哥的教师公寓，就是五栋四单元614。

也就是说，那间房子已经被他哥租出去了？还租给了一个女生？

那女生回来后，⻅到自己家里有动静，就悄咪咪的出去报了警。

一波分析，事件水落石出，洛野恍然大悟。

服了。

顾明轩六个小时的飞机，现在至少还要三个小时落地，他要在警察局里蹲三个小时。

很快，一个年迈警察走了进来，看上去很有阅历的样子。

年轻警察让出了位置，喊了一声“所⻓”。

洛野震惊。

所⻓？派出所老大亲自来审他？

这下哪怕洛野真没犯事，心里也有一点点小担忧。

只⻅这个年纪大的警察递给年轻警察一份资料，年轻警察一看，神色一变。

这是洛野的资料。

烈士之子，父母都是警察，牺牲在任务中，由小姨抚养长大，是顾明轩的表弟。

虽然是个表的，但两人一起长大，跟亲兄弟没什么区别。

难怪所⻓亲自来了。

“小伙子，这次是我们误会你了。”

“没。”

洛野弱弱的不敢说话。

所⻓欣慰的看着洛野，赞叹道：“江大也是名校，以后好好学习，报效国家。”

洛野点了点头。

然后拒绝了所长亲切的留宿邀请，只是吃了顿晚饭就出来了。

江城的夜晚阴凉，九月的天格外清爽。

洛野的心情却是郁闷的。

明天就开学了，他发现学校附近的酒店都被住满了，而教师公寓肯定是回不去了。

这叫什么事儿。

他跨越一千七百多公里，从京城来到江城上大学，还没开始就去派出所半日游，晚上还没地方住。

nice，完美的开端。

很快，一阵凉风吹过，毛毛细雨落在洛野的头上。

洛野躲在一棵树下，他掏出手机，点开了跟女神的聊天界面，将今天的事情分享给对方。

但是对方并没有回复他。

洛野翻看了聊天记录，随后叹了口气。

自从他将自己考上江城大学的事情告诉对方后，对方就没有回复过他了。

也许……从头到尾都是他在自作多情吧。

他隐隐之间也能猜到了，对方只是找了个拒绝他的理由。

如果他还这么不懂事的话，那就是他的不对了。

高三毕业后的暑假，有整整三个月，这三个月的时间，也许他早就不喜欢自己的女神了，只是心中有一丝丝不甘心而已。

如今他已经是大学生了，既然如此，也该开始新的生活了。

话说，江城的雨还真是多呢，还是先找个网咖凑合一下吧。

洛野拿着身份证，开了一台电脑。

这家网咖在学校对面，很方便，明天醒来就能直接去报名了。

打开电脑，洛野点开了西红柿小说，开始码字。

说起来，他也算是小有名气的网文作者，笔名[落叶归根]，暑假三个月的时间，他的第一本恋爱小说火了。

作为即将成为大学生的年龄，他如今的稿费十分可观，已经让他没有什么压力了。

第二天。

依旧下着小雨，江城大学开学季，洛野先来到了教师公寓。

看着眼前614的房⻔，洛野轻轻地敲了敲，没有回应，然后他又敲了敲，还是没有。

犹豫片刻，洛野拿出钥匙，打开了房门。

自己昨晚留在这里的行李箱还放在客厅中，上面还有一张留言条。

：抱歉，我也是最近刚租这间房子，因为房东已经出国了，听到屋子里有动静我以为是小偷。

字迹工整，很漂亮。

他昨天打游戏太认真了，连进来人都不知道，也活该自己被抓起来。

洛野把纸条塞进了包里，然后离开了这里，前往江城大学的校门口。

本来是开学第一天，却下起了雨，雨势越来越大，一个学姐撑着伞走了过来。

“是学弟吗？录取通知书看一看。”

洛野从包里拿出录取通知书，这位学姐看了一眼。

“计算机专业洛野。”

学姐看了看洛野帅气的脸庞，整个人更为热情了一分。

“来学弟，跟着学姐走。”

在学姐热情的带领下，洛野完成了报名，找到了自己的寝室。

八栋515，拒绝了学姐的约饭请求，告别了学姐，洛野走进了寝室。

未来的三个室友还没有来，听说外地新生九月一日报名，而省内新生是九月二日，所以他们明天才会来。

把床铺整理好后，洛野寻思着等明天室友来了再进行一些寝室布局。

突然，电话铃声响了起来，一看来电人是顾明轩，洛野接通电话。

“小洛，有件事情跟你说一下，教师公寓你别去了，我出国这两年期间把它租出去了。”

“......我昨天去了。”

电话那头一阵沉默，随后说道：“她没把你怎么样吧？”

“没，就是给我整局子里了。”

“噗，不愧是她。”

“小洛，她是我学生，在江大，你以后早晚会认识她，小姑娘挺不错的，就是性格不太好相处。”

挂断了电话，洛野走到了阳台，一缕阳光照射进来。

雨停了。

出去溜达溜达吧。

洛野在江大闲逛。

江大最宏伟的建筑，自然是图书馆，正对着学校大门，是江大的排面。

图书馆入口，看着眼前的人脸识别自动⻔，洛野陷入了沉思。

这时，一个身材高挑，留着黑色⻓直发，穿着宽松牛仔裤的女生，迈着大⻓腿从洛野身旁绕了过去。

别问为什么宽松牛仔裤洛野还能看出来是大长腿，有些东西是衣服掩盖不了的。

洛野没有看到女生的⻓相，但是仅看她的背影就能让人产生无限遐想。

女生⻘丝浸濡，衣物微湿，手中提着的白色电脑包也带着些许水渍，很明显是刚刚淋着雨进来的。

“学姐！”

洛野叫住了她。

女生侧身回头，神色平淡的看了一眼洛野。

“你在叫我？”

女生微微开口，声音不大。

洛野看到女生的⻓相，心中忍不住惊叹。

他早就听说江城出美人，却没想过刚来到学校就遇到了如此美丽的女孩。

对方没有化妆，但依旧娉婷婀娜，说是沉⻥落涯，闭月羞花也不为过。

洛野嘴笨，不太爱说话，没谈过恋爱，也容易害羞。

“学姐……能……能帮我刷……刷一下脸吗?”

女生微微一愣，她站在人脸识别前。

下一刻。

电子⻔禁打开。

“你先进。”

“谢谢学姐。”

洛野像个害羞的大男孩一样走了进去。

女生诧异的看了一眼洛野，没想到他叫住自己竟然真的只是让自己帮忙刷一下脸。

说实话，洛野是她今天⻅到的第五个新生。

但是前四个新生，都是为了要她的联系方式。

“粥粥，走那么快干嘛。”

另一个女孩小跑了过来，相比于前者，这个女孩并没有那么惊艳，但是依旧是一位不可多得美女。

她叫秦钰雯，经管学院大三年级，也是经管学院的院花。

眼前这位是她的闺蜜，名叫苏白粥，江城大学校学生会会长。

同时，也是江大唯一校花，以冰山美人著称的一位工作狂，计算机专业十年难遇的绝世美女。

“新生的事情比较多。”苏白粥平淡说道。

“说起来，昨天那件事情的后续是什么?小偷有没有被绳之以法？”

“一场误会。”

苏白粥面色不变。

警察已经把前因后果跟她解释了一遍。
"""
    action = DesignNovelRoles(content=content)
    result = await action.run()
    print('res:', result)


if __name__ == '__main__':
    asyncio.run(main())
