from google.cloud import bigquery, storage
import pandas as pd
import joblib
from sklearn.metrics import r2_score

# --- 設定値 ---
PROJECT_ID = "PROJECT_ID"#（あなたの環境に合わせて変更） 
BQ_TABLE_PATH = f"{PROJECT_ID}.StudentsPerformance0919.StudentsPerformanceTable"
GCS_BUCKET_NAME = "GCS_BUCKET_NAME" #（あなたの環境に合わせて変更） 

MODEL_PATHS = {
    "LinearRegression": "models/math_predictor/v1/LinearRegression.pkl",
    "LightGBM": "models/math_predictor/v1/LightGBM.pkl"
}

def evaluate_model(model_name, model, X, y):
    """各モデルのスコア計算を行う"""
    y_pred = model.predict(X)
    score = r2_score(y, y_pred)
    print(f" {model_name} の R²スコア: {score:.3f}")
    if score < 0.7:
        print(f" {model_name} の精度が低下しています。再学習を検討してください。")
    return score

def main():
    print("=== モデル自動スコアチェック開始 ===")

    # BigQueryから最新データ取得
    bq = bigquery.Client(project=PROJECT_ID)
    df = bq.query(f"SELECT * FROM `{BQ_TABLE_PATH}`").to_dataframe()
    print(f" BigQueryから{len(df)}件のデータを取得しました")

    X = pd.get_dummies(df.drop("math_score", axis=1), drop_first=True)
    y = df["math_score"]

    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(GCS_BUCKET_NAME)

    results = {}

    for model_name, model_path in MODEL_PATHS.items():
        try:
            blob = bucket.blob(model_path)
            local_path = f"{model_name}.pkl"
            blob.download_to_filename(local_path)
            model = joblib.load(local_path)

            score = evaluate_model(model_name, model, X, y)
            results[model_name] = score

        except Exception as e:
            print(f" {model_name} の評価に失敗しました: {e}")

    print("\n=== 評価完了 ===")
    for name, score in results.items():
        print(f"{name}: R² = {score:.3f}")

if __name__ == "__main__":
    main()
