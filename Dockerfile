FROM python:3.10 as builder

WORKDIR /home/SuperAssistent_Server

COPY requirements.txt requirements.txt
#RUN  pip install --upgrade pip
#RUN  pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

RUN pip install -r requirements.txt

COPY app_server app_server
COPY app_agents app_agents
COPY feishu_utils feishu_utils
COPY MetaGPT MetaGPT
COPY migrations migrations
#COPY config.py agents_config.json  ./
#COPY app.py   ./
#COPY fssl.key fssl.pem ./

CMD ["flask","db","upgrade"]
#CMD ["python", "init_db.py"]   #初始化数据库
CMD ["python", "app.py"]
