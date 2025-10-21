# --- 1. ベースイメージ ---
FROM python:3.9-slim

# --- 2. LightGBM依存ライブラリ ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# --- 3. 作業ディレクトリ ---
WORKDIR /app

# --- 4. 必要ライブラリ ---
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- 5. スクリプトのコピー ---
COPY monitor.py .

# --- 6. Cloud Run 実行コマンド ---
CMD ["python", "monitor.py"]