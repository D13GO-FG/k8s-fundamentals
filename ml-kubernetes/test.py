import json

import requests

url = "http://127.0.0.1:49277/v2/models/mlflow-model/infer"

payload = json.dumps(
    {
        "inputs": [
            {
                "name": "input",
                "shape": [-1,13],
                "datatype": "FP64",
                "data": [[14.23, 1.71, 2.43, 15.6, 127.0, 2.8, 3.06, 0.28, 2.29, 5.64, 1.04, 3.92, 1065.0]]
            }
        ]
    }
)
response = requests.post(
    url=url,
    data=payload,
    headers={
        "Host": "mlflow-wine-classifier-mlflow-kserve-test.example.com",
        "Content-Type": "application/json",
    },
)
print(response.json())
