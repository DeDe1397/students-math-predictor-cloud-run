# --- 1. ベースイメージ ---
FROM python:3.9-slim

# --- 2. LightGBM 依存パッケージ ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# --- 3. 作業ディレクトリ ---
WORKDIR /app

# --- 4. Pythonライブラリ ---
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- 5. アプリのコピー ---
COPY app.py .

# --- 6. Streamlit実行設定 ---
EXPOSE 8080
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]