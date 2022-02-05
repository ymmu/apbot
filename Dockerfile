FROM python:3.9

# create & move a directory or move to here
WORKDIR /data/lucca/apps/apbot
# VOLUME $APBOT/logs


# -qq 로그 출력 안 하게
RUN apt-get -qq update \
    && apt-get -y -qq install git gcc wget\
    #&& git clone https://github.com/ymmu/apbot.git \
    && python -m pip install --upgrade pip \
    && python -m pip install -q "pymongo[encryption,srv]~=3.11" \
    && python3 -m pip install -q --upgrade Pillow \
    && wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y -qq ./google-chrome-stable_current_amd64.deb

# 소스 카피 혹은 깃에서 땡겨와도 될거같다
COPY . .
RUN pip install -r ./requirements.txt

ENV APBOT /data/lucca/apps/apbot
ENV PATH $APBOT/mongodb-linux-x86_64-enterprise-ubuntu2004-4.4.12/bin:$PATH

WORKDIR $APBOT
ENTRYPOINT ["python","main.py"]
