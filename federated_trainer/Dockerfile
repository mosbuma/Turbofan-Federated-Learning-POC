FROM heurekalabs/syft-base

RUN apt-get --allow-releaseinfo-change update && \
    apt-get install -y gnuplot && \
    apt-get clean

COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 install -r requirements.txt

COPY . /app
WORKDIR /app
RUN rm -f /app/**/*.db

RUN mkdir -p /models
RUN chown -R root:root /models

ENTRYPOINT ["sh", "entrypoint.sh"]
