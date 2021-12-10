from fastapi import (
    FastAPI,
    HTTPException,
    Header,
    Request,
    Depends,
    File,
    UploadFile,
)
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import re
import pandas as pd
import time
import datetime
from enum import Enum
import pickle
import glob
import base64
import binascii
import uvicorn

from train.train import get_processed_data, clean_rows, get_preprocessor

api = FastAPI(
    title="API Models",
    description="""This API allow to get predictions from trained
     Machine Learning models
    """,
    version="1.0.0",
)


credentials = [
    b"alice:wonderland",
    b"bob:builder",
    b"clementine:mandarine",
    b"admin:4dm1N",
]

# retrieve data to provide score with models
X_train, X_test, y_train, y_test = get_processed_data()

auth_header = Header(
    default="Basic ",
    description="""authorization header need to contain
    credentials of user (username:password)""",
)


class Models(Enum):
    """
    Possible values for models
    """

    lgbm = "LGBMClassifier"
    logistic = "LogisticRegression"
    gaussian = "GaussianNB"
    knn = "KNeighborsClassifier"
    forest = "RandomForestClassifier"
    lineardiscriminant = "LinearDiscriminantAnalysis"
    svc = "SVC"
    decisiontree = "DecisionTreeClassifier"


class ModelsName(BaseModel):
    """
    Name of the model used by the request
    """

    model_name: Models


def get_models_dict() -> dict:
    """
    Return the dict of available models
    """
    model_files = glob.glob("ml_models/*_trained")
    models = {}

    for file_model in model_files:
        with open(file_model, "rb") as mod_file:
            model = pickle.load(mod_file)

        models[type(model).__name__] = model

    return models


def get_models_list() -> list:
    """
    Return the list of available models
    """
    return list(get_models_dict().keys())


def check_authorization(authorization_header=auth_header):
    """
    Function to check authorization-header and validate the credentials
    """
    if "Basic " not in authorization_header:
        raise HTTPException(
            status_code=400, detail="Invalid authorization header"
        )

    authorization_string = re.search("Basic .*", authorization_header)

    if authorization_string is None:
        authorization_bytes = None
    else:
        authorization_bytes = (
            authorization_string.group().split("Basic")[1].strip().encode()
        )

    try:
        authorization_decoded = base64.decodebytes(authorization_bytes)
    except (binascii.Error, TypeError):
        raise HTTPException(status_code=400, detail="Invalid base64 string")

    if (
        authorization_decoded is None
        or authorization_decoded not in credentials
    ):
        raise HTTPException(
            status_code=403,
            detail="You do not have authorization to acces this ressource",
        )


models_dict = get_models_dict()

# Endpoints


@api.get("/", name="Check API")
def index() -> dict:
    """
    Return a dictionnary that indicate the api is running
    """

    return {"status": "running"}


@api.get("/info", name="Get informations")
def get_info(authorization_header=Depends(check_authorization)) -> dict:
    """
    Return informations on the API
    """

    # Return models list
    return {"models": get_models_list()}


@api.post("/score", name="Get performance score for a model")
def score(
    modelsname: ModelsName, authorization_header=Depends(check_authorization)
) -> dict:

    return {
        "score": models_dict[modelsname.model_name.value].score(X_test, y_test)
    }


@api.post("/predict/{model_name}", name="Get prediction from given data")
def predict(
    model_name: Models,
    file: UploadFile = File(...),
    authorization_header=Depends(check_authorization),
) -> dict:

    if file.content_type != "text/csv":
        raise HTTPException(
            status_code=400,
            detail="Wrong file type or type not specified."
            + "Only csv files are accepted",
        )

    dataframe = pd.read_csv(file.file)

    dataframe = clean_rows(dataframe)

    X_predict = dataframe.drop(["RainTomorrow"], axis=1)

    preprocessor = get_preprocessor()

    X_predict = preprocessor.transform(X_predict)

    return {
        "prediction": models_dict[model_name.value].predict(X_predict).tolist()
    }


if __name__ == "__main__":
    uvicorn.run(
        "api_models:api",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="warning",
    )
