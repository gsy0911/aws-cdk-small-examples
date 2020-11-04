# ここはビルド用のコンテナ
FROM python:3.8-buster as builder

WORKDIR /opt/app

COPY requirements.txt /opt/app
RUN pip3 install -r requirements.txt

# ここからは実行用コンテナの準備
FROM python:3.8-slim-buster as runner

COPY --from=builder /usr/local/lib/python3.8/site-packages /usr/local/lib/python3.8/site-packages
COPY src /opt/app/src

WORKDIR /opt/app/src
CMD ["python3", "__init__.py"]