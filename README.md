#  学生の成績予測アプリ (Streamlit + Cloud Run)

このプロジェクトは、Kaggle「Students Performanca in Exams」のデータセットを活用し、
学生の様々な属性（性別、人種、親の学歴など）と、中間スコア（リーディング、ライティング）を入力として、
最終的な成績（数学のスコア）を予測する機械学習Webアプリケーションです。
Google Cloud Platform (GCP) の **Cloud Run** を利用して、サーバーレスでコンテナ化されたStreamlitアプリとしてデモ公開しています。

##  デモ

https://streamlit-math-predictor-218616351259.asia-northeast1.run.app/

##  目的

スコアのみならず、講座の受講状況など他の要因も踏まえて、予測値を算出し、
その結果をもとに、改善点を示したり、追加受講を課したりするなど、
効率性向上や個別学習プランの作成につなげるといった施策への要因補助がねらいです。

##  免責事項

このアプリは教育目的のデモンストレーション用であり、実際の生徒データを使用していません。

---

##  動作環境とデプロイ方法

このアプリをGCPのCloud Runにデプロイする手順は以下の通りです。


### 1. 必要なツール

デプロイには以下のツールが必要です。

* **Google Cloud CLI (`gcloud`)**
* **Git**
* **Docker** 

### 2. 環境設定

1.  **GCPプロジェクトIDの設定**
    ```bash
    gcloud config set project YOUR_PROJECT_ID
    ```
2.  **必要なAPIの有効化**
    Cloud Run、Cloud Build、Artifact Registry のAPIを有効化します。

### 3. IAMロールの確認と付与

コンテナのビルドとデプロイに使用するサービスアカウントに、以下のロールが付与されていることを確認してください。

* `[プロジェクト番号]-compute@developer.gserviceaccount.com` に対して:
    * `Cloud Build サービス アカウント`
    * `Artifact Registry 書き込み`
* Cloud Runサービスのサービスアカウントに対して:
    * `Storage オブジェクト閲覧者` (モデルファイル `model.pkl` へのアクセスに必要)

### 4. アプリケーションのデプロイ

`app.py`、`requirements.txt`、`Dockerfile`、`model.pkl` が全て存在するディレクトリで、以下のコマンドを実行します。

```bash
gcloud run deploy streamlit-math-predictor \
    --source . \
    --region asia-northeast1 \
    --platform managed \
    --allow-unauthenticated \
    --project YOUR_PROJECT_ID
```

###  5.注意事項（デプロイと再現性について）

- **学習済みモデルの非公開:** 学習済みモデルファイル（`model.pkl` および `feature_list.pkl`）は、機密保持に従い、GitHub上では公開していません。
- **再現方法:** 本プロジェクトを再現される際は、同梱の **`Linear.ipynb`** を実行し、ご自身の環境でモデルを再学習してください。
- **データの前処理:** BigQueryなどの環境で問題が発生しないよう、コード内では列名のスペースをアンダースコア (`_`) に変換する処理を行っています。
- **同梱の **`Linear.ipynb`** にあるPROJECT_ID,BQ_TABLE_PATH,GCS_BUCKET_NAMEについてはご自身の環境に応じて入力をしてください。  

##  機械学習・アプリ化
###  1. 使用技術
- **フロントエンド**: Streamlit
- **機械学習**: LinearRegression, scikit-learn
- **インフラ**: Google Cloud Run, Docker
- **言語**: Python

###  2. データ
- Kaggle: Students Performance in Exams
- 再現のため、以下の手順でご自身のGCPプロジェクトのBigQueryにデータを取り込んでください。
  * GCPコンソールでBigQueryサービスに移動します。
  * **ご自身のデータセット**を作成し、そのデータセット内にダウンロードしたCSVファイルからテーブルを作成します。
  * このテーブルのパスを **`Linear.ipynb`** の `BQ_TABLE_PATH` 変数に設定してください。

###  3. モデル性能
- train_R2 スコア: 0.8812
- test_R2 スコア: 0.8553
