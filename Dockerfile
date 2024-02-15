FROM python:3

ARG GRADIO_SERVER_PORT=7860

WORKDIR /usr/src/app


COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV GRADIO_SERVER_PORT=${GRADIO_SERVER_PORT}
ENV GRADIO_SERVER_NAME='0.0.0.0'
EXPOSE ${GRADIO_SERVER_PORT}

CMD [ "python3", "./app.py" ]
