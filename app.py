import streamlit as st
import pandas as pd
import joblib
from google.cloud import storage
import os

# --- 設定値 ---
GCS_BUCKET_NAME = "GCS_BUCKET_NAME" #（あなたの環境に合わせて変更） 
GCS_MODEL_PATH = "models/math_predictor/v1/math_score_model.pkl"
GCS_FEATURE_PATH = "models/math_predictor/v1/feature_list.pkl"

# Streamlitアプリに利用規約
st.warning("⚠️ このアプリはデモ用です。商用利用は禁止されています。")

# --- モデルと特徴量リストのロード ---
@st.cache_resource
def load_model_artifacts():
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        model_blob = bucket.blob(GCS_MODEL_PATH)
        model_blob.download_to_filename("model.pkl")
        model = joblib.load("model.pkl")
        feature_blob = bucket.blob(GCS_FEATURE_PATH)
        feature_blob.download_to_filename("feature_list.pkl")
        feature_list = joblib.load("feature_list.pkl")
        
        return model, feature_list
    except Exception as e:
        st.error(f"モデルまたは特徴量リストのロードに失敗しました: {e}")
        return None, None

model, feature_list = load_model_artifacts()

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
    return prediction[0]

# --- Streamlit UI ---
st.title('📐 数学スコア予測アプリ')
st.markdown('線形回帰モデルから予測値を計算します。')

if model is not None:
    with st.form("prediction_form"):
        st.header("生徒の情報入力")
        
        gender = st.selectbox('性別', ['male', 'female'])
        race = st.selectbox('人種/民族', ['group A', 'group B', 'group C', 'group D', 'group E'])
        education = st.selectbox('親の学歴', ["some high school", "high school", "some college", "associate's degree", "bachelor's degree", "master's degree"])
        lunch = st.selectbox('昼食', ['standard', 'free/reduced'])
        prep_course = st.selectbox('試験準備コース', ['none', 'completed'])

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
        
        predicted_score = get_prediction(input_data, model, feature_list)
        
        st.success(f"### 予測された数学のスコアは **{predicted_score:.1f}** 点です。")

else:
    st.warning("モデルのロードに失敗しているため、予測を実行できません。GCSバケット名と権限を確認してください。")