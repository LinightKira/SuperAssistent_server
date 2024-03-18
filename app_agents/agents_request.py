from app_agents.roles.write_prd_to_feishu import start_write_prd_to_feishu


async def get_metagpt_agents_result(input_data, agent_name):
    print('start agent:', agent_name)
    print('input_data:', input_data)
    if agent_name == 'WritePRD':
        res = await start_write_prd_to_feishu(input_data)
        return res
    else:
        return "ok"
