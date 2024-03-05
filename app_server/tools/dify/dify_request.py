import requests

import config

"""
Generate a POST request to the DIFY API based on the provided API key, payload, and mode.

Parameters:
- api_key (str): The API key for authentication.
- payload (dict): The data to be sent in the request body.
- mode (str): The mode of the request, either 'completion' or 'chat'.

Returns:
- response: The response object from the POST request.
"""


def Make_dify_request(api_key, payload, mode='completion'):
    base_url = config.Config.DIFY_BASE_URL

    if mode == 'completion':
        url = base_url + 'completion-messages'
    elif mode == 'chat':
        url = base_url + 'chat-messages'
    else:
        raise ValueError("Invalid mode. Use 'completion' or 'chat'.")

    isStreaming = payload.get('response_mode') == 'streaming'
    # print('isStreaming:', isStreaming)

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    # print('payload:', payload)
    # print('headers:', headers)
    # print('url:', url)
    response = requests.post(url, headers=headers, json=payload, stream=isStreaming)

    return response
