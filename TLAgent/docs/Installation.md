# 所需环境
Python==3.10.0
pip install -r requirements.txt

# 修改配置文件
将Redis和PostgreSQL路径配置到config.yaml当中
redis建议安装在linux系统当中。

# 同步postgreSQL数据库
alembic upgrade head

# 创建用户和组织
python tfagent/exp_controllers/addUserwithorg.py

# 向对应组织添加模型API
python tfagent/exp_controllers/addmodelwithAPIkey.py

# 往数据库导入自定义的agent workflow
python tfagent/exp_controllers/addworkflows.py

# 向数据库中导入工具集
python tfagent/exp_controllers/addtoolkits.py

# 启动celery
## linux启动celery 4.x
celery -A tfagent.worker worker --beat --loglevel=info

## windows 启动celery 4.x +
pip install eventlet
celery -A tfagent.worker worker --loglevel=info -P eventlet

# 设置task 将task发送至celery服务中
python tfagent/exp_controllers/tf_creater.py


