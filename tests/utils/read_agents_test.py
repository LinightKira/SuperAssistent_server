from app_server.tools.file_tools import read_json_from_file

json_data = read_json_from_file("../../agents_config.json")
print("\033[95m\033[1m" + "\n*****Agents config*****\n" + "\033[0m\033[0m")
print('json_data:', json_data)
print('main_api_key:', json_data['main_api_key'])