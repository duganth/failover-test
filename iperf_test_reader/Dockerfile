FROM  python:3.7.7-alpine3.11 as base 
RUN apk add --no-cache iproute2 
RUN apk add --no-cache iperf3

WORKDIR /app/

from base as dependencies
COPY ./requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

FROM dependencies as run
COPY ./main.py /app/
ENTRYPOINT ["python", "main.py"] 
