FROM python:3.9

# create & move a directory or move to here
WORKDIR /data/lucca/apps
# VOLUME $APBOT/logs

# 소스 카피 혹은 깃에서 땡겨와도 될거같다
# COPY /data/lucca/apps/apbot .

RUN apt-get -qq update && apt-get -y install git gcc vim \
    && git clone https://github.com/ymmu/apbot.git \
    && pip install -f ./requirements.txt

ENV PATH /data/lucca/apps/mongodb-linux-x86_64-enterprise-ubuntu2004-4.4.12/bin:$PATH
ENV APBOT /data/lucca/apps/apbot
ENTRYPOINT ["python","$APBOT/main.py"]

