# 1. ベースイメージの指定 (FROM)
FROM python:3.9-slim 

# 2. 作業ディレクトリの設定 (WORKDIR)
WORKDIR /app

# 3. 依存関係のコピーとインストール (COPY & RUN)
COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt

# 4. アプリケーションコードのコピー (COPY)
COPY app.py .

# 5. アプリの実行コマンドの定義 (ENTRYPOINT)
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]