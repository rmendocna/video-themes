FROM python:alpine3.7
RUN apk add mongodb
COPY . /app
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 8000
# RUN gunicorn project:'create_app()'
# ENTRYPOINT [ "python" ]
# CMD [ "demo.py" ]
