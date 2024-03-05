"""
@Time        : 2023/12/20 11:38
@Author      : LinightX
@File        : logger.py
@Description : 日志包
"""

# 创建日志器
import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

logger_runner = logging.getLogger("happiness")

# 设置日志级别
logger_runner.setLevel(logging.INFO)

# 自动创建目录
if not os.path.exists('logs'):
    os.makedirs('logs')

# 定义日志文件的名称和位置
log_file = 'happiness__{date}.log'.format(date=datetime.now().strftime('%Y-%m-%d'))
log_dir = 'logs'

# 创建 handlers
c_handler = logging.StreamHandler()
f_handler = TimedRotatingFileHandler(os.path.join(log_dir, log_file), when='midnight', interval=1, backupCount=30,
                                     encoding='utf-8')
c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.INFO)

# 创建格式器并添加到handlers
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
f_format.encoding = 'utf-8'  # 设置编码

c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# 添加 handlers到日志器
logger_runner.addHandler(c_handler)
logger_runner.addHandler(f_handler)
