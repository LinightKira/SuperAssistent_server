from app_server.routes.assistant import extract_action_info

input_data = '''
Question: Can you help me write a product requirement document to increase the playback duration?
Thought: I should use the WritePRD tool to create a detailed document outlining the requirements for extending the playback duration.
Action:
{
"action": WritePRD,
"action_input": "Product requirement document to increase playback duration"
}
'''

action, action_input = extract_action_info(input_data)
print('action:', action)
print('action_input:', action_input)
