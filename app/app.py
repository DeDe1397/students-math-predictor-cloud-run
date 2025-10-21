import streamlit as st
import pandas as pd
import joblib
import shap
import matplotlib.pyplot as plt
from google.cloud import storage
import os
import numpy as np

# --- 設定値 ---
GCS_BUCKET_NAME = "GCS_BUCKET_NAME" #（あなたの環境に合わせて変更） 
MODEL_PATHS = {
    "LinearRegression": "models/math_predictor/v1/LinearRegression.pkl",
    "LightGBM": "models/math_predictor/v1/LightGBM.pkl"
}
GCS_FEATURE_PATH = f"models/math_predictor/v1/feature_list.pkl"


st.warning("⚠️ このアプリはデモ用です。商用利用は禁止されています。")

# --- データ生成関数 ---
def create_background_data(feature_list, n_samples=100):
    data = {}
    for feature in feature_list:
        if feature in ['reading_score', 'writing_score']:
            data[feature] = np.random.uniform(50, 100, n_samples)
        else:
            data[feature] = np.random.choice([0, 1], n_samples, p=[0.8, 0.2])
    
    df = pd.DataFrame(data, columns=feature_list)
    return df

# --- モデルと特徴量リスト、Explainerのロード（キャッシュ） ---
@st.cache_resource
def load_model_artifacts(model_name):
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCS_BUCKET_NAME)

        local_model_path = f"{model_name}.pkl"
        if not os.path.exists(local_model_path):
            model_blob = bucket.blob(MODEL_PATHS[model_name])
            model_blob.download_to_filename(local_model_path)
        model = joblib.load(local_model_path)

        feature_blob = bucket.blob(GCS_FEATURE_PATH)
        feature_blob.download_to_filename("feature_list.pkl")
        feature_list = joblib.load("feature_list.pkl")
        
        background_data = None
        explainer = None
        
        if model_name in ["LightGBM", "LinearRegression"]:
            background_data = create_background_data(feature_list, n_samples=100)

            if model_name == "LightGBM":
                explainer = shap.TreeExplainer(model, background_data)
            elif model_name == "LinearRegression":
                explainer = shap.LinearExplainer(model, background_data)
        
        return model, feature_list, explainer
    except Exception as e:
        st.error(f"モデルまたは特徴量リストのロードに失敗しました: {e}")
        return None, None, None

# --- 予測関数 ---
def get_prediction(input_data_dict, model, feature_list):
    input_df = pd.DataFrame([input_data_dict])

    data_for_predict = pd.DataFrame(0, index=[0], columns=feature_list)
    
    data_for_predict['reading_score'] = input_df['reading_score'][0]
    data_for_predict['writing_score'] = input_df['writing_score'][0]
    
    for col in input_df.columns:
        if col not in ['reading_score', 'writing_score']:
            dummy_col_name = f"{col}_{input_df[col][0]}"
            if dummy_col_name in feature_list:
                data_for_predict[dummy_col_name] = 1

    prediction = model.predict(data_for_predict)
    return prediction[0], data_for_predict

# --- Streamlit UI ---
st.title('数学スコア予測アプリ')
st.markdown('線形回帰 or LightGBM を選んで予測とSHAP値を表示します。')

model_choice = st.radio("使用するモデルを選択してください", ["LinearRegression", "LightGBM"])
model, feature_list, explainer = load_model_artifacts(model_choice) 

# --- 再読み込みボタン ---
if st.button("最新モデルを再読み込み"):
    st.cache_resource.clear() 
    model, feature_list, explainer = load_model_artifacts(model_choice)
    if model is not None:
        st.success("最新モデルを読み込みました！")

if model is not None:
    with st.form("prediction_form"):
        st.header("生徒の情報入力")
        
        gender = st.selectbox('性別（gender）', ['male', 'female'])
        race = st.selectbox('人種/民族（race/ethnicity）', ['group A', 'group B', 'group C', 'group D', 'group E'])
        education = st.selectbox('親の学歴（parental_level_of_education）', ["some high school", "high school", "some college", "associate's degree", "bachelor's degree", "master's degree"])
        lunch = st.selectbox('昼食（lunch）', ['standard', 'free/reduced'])
        prep_course = st.selectbox('試験準備コース（test_preparation_course）', ['none', 'completed'])

        reading_score = st.slider('読解のスコア', 0, 100, 70)
        writing_score = st.slider('作文のスコア', 0, 100, 65)

        submitted = st.form_submit_button("予測を計算")

    if submitted:
        input_data = {
            'gender': gender,
            'race/ethnicity': race,
            'parental_level_of_education': education,
            'lunch': lunch,
            'test_preparation_course': prep_course,
            'reading_score': reading_score,
            'writing_score': writing_score
        }
        
        predicted_score, input_encoded = get_prediction(input_data, model, feature_list)
        st.success(f"### 予測された数学のスコアは **{predicted_score:.1f}** 点です。")

        # --- SHAP値の可視化（LightGBM / LinearRegression） ---
        if explainer is not None:
            shap_values = explainer(input_encoded)
            
            st.write("### 予測の理由：それぞれの要因が結果にどれだけ貢献したか")
            
            fig, ax = plt.subplots(figsize=(8, 6))
            shap.plots.waterfall(shap_values[0,:], max_display=10, show=False)
            st.pyplot(fig)
            plt.close(fig)
        
        elif model_choice in ["LightGBM", "LinearRegression"] and explainer is None:
            st.error("SHAP Explainerの初期化に失敗しました。")
            
else:
    st.warning("モデルのロードに失敗しているため、予測を実行できません。GCSバケット名と権限を確認してください。")

