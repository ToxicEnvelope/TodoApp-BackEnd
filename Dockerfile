FROM python:3.8-alpine3.13

RUN apk add --update build-base && /usr/local/bin/python -m pip install --upgrade pip

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

RUN apk del build-base && \
    rm -rf /var/cache/apk/*

EXPOSE 9000
CMD ["todo_restful_app.py"]
ENTRYPOINT ["python3"]