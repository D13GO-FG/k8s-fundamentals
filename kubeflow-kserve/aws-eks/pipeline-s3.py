from kfp import dsl
from kfp import compiler
from kfp.dsl import Input, Output, Dataset, Model
import os


# Step 1: Load Dataset
@dsl.component(base_image="python:3.9")
def load_data(output_csv: Output[Dataset]):
    import subprocess

    subprocess.run(["pip", "install", "pandas", "scikit-learn"], check=True)

    from sklearn.datasets import load_iris
    import pandas as pd

    iris = load_iris()
    df = pd.DataFrame(data=iris.data, columns=iris.feature_names)
    df["target"] = iris.target

    # Save the dataset to the output artifact path
    df.to_csv(output_csv.path, index=False)


# Step 2: Preprocess Data
@dsl.component(base_image="python:3.9")
def preprocess_data(
    input_csv: Input[Dataset],
    output_train: Output[Dataset],
    output_test: Output[Dataset],
    output_ytrain: Output[Dataset],
    output_ytest: Output[Dataset],
):
    import subprocess

    subprocess.run(["pip", "install", "pandas", "scikit-learn"], check=True)

    import pandas as pd
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split

    # Load dataset
    df = pd.read_csv(input_csv.path)

    # Handle missing values
    if df.isnull().values.any():
        print("Missing values detected. Handling them...")
        df = df.dropna()  # Drop rows with any NaN values

    features = df.drop(columns=["target"])
    target = df["target"]

    # Standardize features
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        scaled_features, target, test_size=0.2, random_state=42
    )

    # Create DataFrames for train and test sets
    X_train_df = pd.DataFrame(X_train, columns=features.columns)
    y_train_df = pd.DataFrame(y_train)
    X_test_df = pd.DataFrame(X_test, columns=features.columns)
    y_test_df = pd.DataFrame(y_test)

    # Save processed train and test data
    X_train_df.to_csv(output_train.path, index=False)
    X_test_df.to_csv(output_test.path, index=False)
    y_train_df.to_csv(output_ytrain.path, index=False)
    y_test_df.to_csv(output_ytest.path, index=False)


# Step 3: Train Model
@dsl.component(
    base_image="python:3.9",
    packages_to_install=["pandas", "scikit-learn", "joblib", "boto3", "s3fs"],
)
def train_model(
    train_data: Input[Dataset],
    ytrain_data: Input[Dataset],
    model_output: Output[Model],
    aws_access_key_id: str,
    aws_secret_access_key: str,
    s3_bucket: str,
    s3_key: str,
    s3_endpoint: str,
    s3_region: str,  # Required for real AWS
) -> str:
    import pandas as pd
    from sklearn.linear_model import LogisticRegression
    from joblib import dump
    import boto3
    import os
    from datetime import datetime
    import json

    # Load training data
    X_train = pd.read_csv(train_data.path)
    y_train = pd.read_csv(ytrain_data.path).values.ravel()  

    # Train model
    model = LogisticRegression()
    model.fit(X_train, y_train)

    # First save model locally
    local_path = model_output.path
    dump(model, local_path)
    print(f"Model saved locally to: {local_path}")

    try:
        # Initialize AWS S3 client
        # Notice we are explicitly using the AWS region and standard endpoint
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=s3_region,
            endpoint_url=s3_endpoint,
        )

        # 3. Rename to standard KServe name
        model_name = "model.joblib"
        os.rename(local_path, model_name)
        
        # 4. Upload to S3
        s3_path = f"{s3_key}/{model_name}"
        print(f"Uploading {model_name} to s3://{s3_bucket}/{s3_path}...")
        
        s3_client.upload_file(model_name, s3_bucket, s3_path)
        print(f"Model uploaded successfully to s3://{s3_bucket}/{s3_path}")
        print(f"Model uploaded successfully to s3://{s3_bucket}/{s3_path}")

        # Create outputs directory if it doesn't exist
        os.makedirs("/tmp/outputs", exist_ok=True)

        # Save S3 path to metadata
        metadata_path = "/tmp/outputs/output_metadata.json"
        model_uri = f"s3://{s3_bucket}/{s3_path}"
        with open(metadata_path, "w") as f:
            json.dump({"model_s3_path": model_uri}, f)

        return model_uri

    except Exception as e:
        print(f"Error uploading to AWS S3: {str(e)}")
        raise


# Step 4: Evaluate Model
@dsl.component(base_image="python:3.9")
def evaluate_model(
    test_data: Input[Dataset],
    ytest_data: Input[Dataset],
    model: Input[Model],
    metrics_output: Output[Dataset],
):
    import subprocess
    subprocess.run(["pip", "install", "pandas", "scikit-learn", "matplotlib", "joblib"], check=True)

    import pandas as pd
    from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
    import matplotlib.pyplot as plt
    from joblib import load

    # Load test data & model
    X_test = pd.read_csv(test_data.path)
    y_test = pd.read_csv(ytest_data.path)
    model = load(model.path)

    # Predict
    y_pred = model.predict(X_test)

    # Generate metrics
    report = classification_report(y_test, y_pred, output_dict=True)
    cm = confusion_matrix(y_test, y_pred)
    accuracy = accuracy_score(y_test, y_pred)

    # Save metrics
    metrics_path = metrics_output.path
    with open(metrics_path, "w") as f:
        f.write(f"Accuracy: {accuracy}\n")
        f.write(str(report))


# Define the pipeline specifically for AWS
@dsl.pipeline(name="Iris-AWS-Hybrid")
def ml_pipeline(
    # Pull credentials from environment variables securely
    aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID", ""),
    aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY", ""),
    
    # EDIT THESE FOR YOUR AWS ACCOUNT (or set them via environment variables):
    s3_bucket: str = os.getenv("AWS_S3_BUCKET", "iris-model-storage-1774322827"),
    s3_key: str = "models/iris",
    s3_endpoint: str = os.getenv("AWS_S3_ENDPOINT", "https://s3.us-west-2.amazonaws.com"),
    s3_region: str = os.getenv("AWS_DEFAULT_REGION", "us-west-2")
):
    # Step 1: Load Dataset
    load_op = load_data()

    # Step 2: Preprocess Data
    preprocess_op = preprocess_data(input_csv=load_op.outputs["output_csv"])

    # Step 3: Train Model & Upload to AWS
    train_op = train_model(
        train_data=preprocess_op.outputs["output_train"],
        ytrain_data=preprocess_op.outputs["output_ytrain"],
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        s3_bucket=s3_bucket,
        s3_key=s3_key,
        s3_endpoint=s3_endpoint,
        s3_region=s3_region
    )

    # Step 4: Evaluate Model
    evaluate_op = evaluate_model(
        test_data=preprocess_op.outputs["output_test"],
        ytest_data=preprocess_op.outputs["output_ytest"],
        model=train_op.outputs["model_output"],
    )


# Compile the pipeline into an S3 specific yaml
if __name__ == "__main__":
    compiler.Compiler().compile(pipeline_func=ml_pipeline, package_path="pipeline-s3.yaml")
