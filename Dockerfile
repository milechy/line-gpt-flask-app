# ベースイメージにPython + Tesseract入りのDebianを指定
FROM python:3.11-slim

# 必要なOSパッケージをインストール（tesseract含む）
RUN apt-get update && \
    apt-get install -y tesseract-ocr tesseract-ocr-jpn libglib2.0-0 libsm6 libxrender1 libxext6 && \
    which tesseract && tesseract --version && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 作業ディレクトリを設定
WORKDIR /app

# アプリファイルをコピー
COPY . /app

# Tesseractコマンドのパスを環境変数で明示
ENV TESSERACT_CMD=/usr/bin/tesseract

# 依存関係をインストール
RUN pip install --no-cache-dir -r requirements.txt

# ポート番号
EXPOSE 5000
ENV PORT=5000

# Flaskアプリを起動
CMD ["gunicorn", "-b", "0.0.0.0:$PORT", "main:app"]