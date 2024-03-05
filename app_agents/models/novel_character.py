class NovelCharacter:
    """角色信息"""

    def __init__(self, name, gender, sd_prompts, lora='', voice=''):
        self.name = name
        self.gender = gender
        self.sd_prompts = sd_prompts
        self.lora = lora
        self.voice = voice
