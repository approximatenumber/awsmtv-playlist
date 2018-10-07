FROM ubuntu:17.10

WORKDIR /app

ENV LC_ALL C
ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN true

ADD requirements.txt /app

RUN apt-get update && apt-get -qqy --no-install-recommends install \
        wget \
        firefox \
        python3-pip \
        python3-setuptools \
        xvfb && \
    wget https://github.com/mozilla/geckodriver/releases/download/v0.19.0/geckodriver-v0.19.0-linux64.tar.gz -O /tmp/geckodriver.tar.gz && \
    tar -xzf /tmp/geckodriver.tar.gz -C /usr/bin && rm -rf /tmp/geckodriver.tar.gz && \
    pip3 install --upgrade pip==9.0.3 && pip3 install -r requirements.txt

ADD app.py /app/    
ENTRYPOINT ["./app.py"]
