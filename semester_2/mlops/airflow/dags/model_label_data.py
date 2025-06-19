from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
import json
import pandas as pd
import joblib
import mlflow
from minio import Minio
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from config import MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, DATA_BUCKET, MODEL_NAME, TMP_DIR



def load_posts_from_minio(**kwargs):
    """Load posts from MinIO bucket."""
    date_prefix = datetime.utcnow().strftime("%Y-%m-%d")
    client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)
    obj = client.get_object(bucket_name=DATA_BUCKET, object_name=f"processed_data/{date_prefix}/cleaned_posts.json")
    content = obj.read().decode('utf-8')
    posts = json.loads(content)

    kwargs["ti"].xcom_push(key="posts", value=posts)

    print(f"Loaded {len(posts)} posts from MinIO.")


def load_model_from_mlflow(model_alias):
    """Download model artifacts from MLflow."""
    model_uri = f"models:/{MODEL_NAME}@{model_alias}"
    local_path = mlflow.artifacts.download_artifacts(artifact_uri=model_uri)

    print(f"Model artifacts downloaded to {local_path} for alias '{model_alias}'.")

    return {
        "model": f"{local_path}/model",
        "tokenizer": f"{local_path}/components/tokenizer",
        "encoder": f"{local_path}/components/encoder/label_encoder.pkl",
        "alias": model_alias
    }


def classify_and_save(**kwargs):
    """Classify posts using the model and save results to MinIO."""
    alias = kwargs['alias']
    date_prefix = datetime.utcnow().strftime("%Y-%m-%d")
    model_info = load_model_from_mlflow(alias)

    tokenizer = AutoTokenizer.from_pretrained(model_info["tokenizer"])
    model = AutoModelForSequenceClassification.from_pretrained(model_info["model"])
    classifier = pipeline("text-classification", model=model, tokenizer=tokenizer)

    encoder = joblib.load(model_info["encoder"])
    id_to_label = {v: k for k, v in encoder.items()}

    # get posts from XCom
    ti = kwargs['ti']
    posts = ti.xcom_pull(task_ids="load_posts", key="posts")
    df = pd.DataFrame(posts)

    preds = classifier(df["text"].tolist(), truncation=True)
    df["label"] = [id_to_label[int(p["label"].replace("LABEL_", ""))] for p in preds]
    df["score"] = [p["score"] for p in preds]

    out_path = f"{TMP_DIR}/label_data_{alias}.json"
    df[["text", "label", "score"]].to_json(out_path, orient="records", force_ascii=False)

    client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)
    client.fput_object(
        bucket_name=DATA_BUCKET,
        object_name=f"model_label_data/{date_prefix}/{alias}/label_data.json",
        file_path=out_path
    )

    print(f"Saved {len(df)} classified posts to MinIO under alias '{alias}'.")


def compare_models(**kwargs):
    """Compare model results for provided aliases."""
    date_prefix = datetime.utcnow().strftime("%Y-%m-%d")
    client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)
    aliases = kwargs["model_aliases"]

    merged = None

    for idx, alias in enumerate(aliases):
        obj = client.get_object(DATA_BUCKET, f"model_label_data/{date_prefix}/{alias}/label_data.json")
        content = obj.read().decode("utf-8")
        df = pd.read_json(content)

        # Rename label and score columns
        df = df.rename(columns={
            "label": f"{alias}_label",
            "score": f"{alias}_score"
        })

        # Keep 'text' only for the first model
        if idx > 0:
            df = df.drop(columns=["text"])

        df.reset_index(drop=True, inplace=True)

        if merged is None:
            merged = df
        else:
            merged = pd.concat([merged, df], axis=1)

    # Save to temp file
    out_path = f"{TMP_DIR}/comparison.json"
    merged.to_json(out_path, orient="records", force_ascii=False)

    # Upload to MinIO
    client.fput_object(
        bucket_name=DATA_BUCKET,
        object_name=f"model_label_data/{date_prefix}/comparison.json",
        file_path=out_path
    )


with DAG(
    dag_id="model_label_data",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["mlflow", "comparison"]
) as dag:

    model_aliases = ["champion", "challenger"]

    load_posts_task = PythonOperator(
        task_id="load_posts",
        python_callable=load_posts_from_minio
    )

    classify_model_tasks = [
        PythonOperator(
            task_id=f"classify_{alias}",
            python_callable=classify_and_save,
            op_kwargs={"alias": alias}
        ) for alias in model_aliases
    ]

    compare_results_task = PythonOperator(
        task_id="compare_results",
        python_callable=compare_models,
        op_kwargs={"model_aliases": model_aliases}
    )

    load_posts_task >> classify_model_tasks >> compare_results_task
