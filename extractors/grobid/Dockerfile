FROM ubuntu

RUN apt-get update && apt-get install -y software-properties-common
RUN echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | debconf-set-selections
RUN add-apt-repository -y ppa:webupd8team/java && \
    apt-get update && apt-get install -y \
        oracle-java8-installer \
    	maven \
    	git \
    	python-pip
RUN pip install supervisor --upgrade

ENV JAVA_HOME "/usr/lib/jvm/java-8-oracle"

RUN git clone https://github.com/kermitt2/grobid.git
RUN cd /grobid && mvn -Dmaven.test.skip=true clean install
RUN echo '#!/bin/sh' > /grobid/run.sh && \
    echo 'cd /grobid/grobid-service' >> /grobid/run.sh && \
    echo 'exec /usr/bin/mvn -Dmaven.test.skip=true jetty:run-war > /tmp/grobid-service.log 2>&1' >> /grobid/run.sh && \
    chmod +x /grobid/run.sh

RUN echo '[supervisord]' > /grobid/supervisor.conf && \
    echo 'logfile=/tmp/supervisord.log' >> /grobid/supervisor.conf && \
    echo '[program:grobid]' >> /grobid/supervisor.conf && \
    echo 'command=/grobid/run.sh' >> /grobid/supervisor.conf && \
    echo 'autorestart=true' >> /grobid/supervisor.conf

EXPOSE 8080

CMD [ "/usr/local/bin/supervisord", "-n", "-c", "/grobid/supervisor.conf" ]
