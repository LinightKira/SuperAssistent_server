class DifyAgent:
    name = ""
    introduction = ""
    api_key = ""
    response_mode = ""
    mode = ""

    def __init__(self, name, introduction, api_key, response_mode, mode):
        self.name = name
        self.introduction = introduction
        self.api_key = api_key
        self.response_mode = response_mode
        self.mode = mode
