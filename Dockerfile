# 父镜像环境拉取
FROM arwineap/docker-ubuntu-python3.6

# 当前目录下的文件添加到镜像中
COPY  . /listen_email

# 设置环境变量
# ENV PATH /Users/zl/PycharmProjects/docker_test/test_docker
# 工作目录指定
WORKDIR /listen_email
ENV LANG C.UTF-8
ENV TZ=Asia/Shanghai
# 安装python相关包
# RUN pip install -r requirements.txt
RUN apt-get update -y && \
    apt-get install -y cron && \
    touch /var/log/cron.log && \
    crontab ./crontab_code && \
    pip install -r requirements.txt

# ADD ./etc/crontab /etc/cron.d/crontab
# EXPOSE 80
# 运行代码
# RUN python3.6 listen_mail.py
# 项目名称环境变量
# 运行docker的时候默认参数配置
# CMD ["python3.6", "listen_email.py"]
# 防止容器自动退出
CMD service cron start && tail -f /var/log/cron.log
