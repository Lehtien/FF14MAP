from fastapi import FastAPI, UploadFile, status, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from pillow_heif import register_heif_opener
from PIL import Image
import imagehash
import json
import mimetypes
import base64

import requests
import io
import re

from concurrent.futures import ProcessPoolExecutor

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def handler(request: Request, exc: RequestValidationError):
    print(exc)
    return JSONResponse(content={"error_message": "予期せぬエラーが発生しました。"}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


def compare_image_hash(input_image_hash, image_hash):
    return input_image_hash - imagehash.hex_to_hash(image_hash)


@app.post("/uploadfile/{select}")
async def upload_file(upload_file: UploadFile, select: str):
    upload_file.file.seek(0, 2)
    if upload_file.file.tell() > 2097152:
        return JSONResponse(content={"error_message": "ファイルサイズは2Mbまでアップロードできます。"}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    if ("image/" not in upload_file.content_type) or (upload_file.content_type != "application/octet-stream"):
        if "image/" not in mimetypes.guess_type(upload_file.filename)[0]:
            return JSONResponse(content={"error_message": "画像のみアップロードできます。"}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    register_heif_opener()
    input_image_hash = imagehash.average_hash(Image.open(upload_file.file))

    with open(f"map_hash/image_hash_{select}.json", "r", encoding="utf-8") as f:
        image_hash_list = json.load(f)

    min = None
    first = None
    second = None
    with ProcessPoolExecutor(max_workers=4) as executor:
        for image_hash in image_hash_list:
            future = executor.submit(compare_image_hash, input_image_hash, image_hash["hash"])
            diff = future.result()

            if min is None:
                min = diff
                first = image_hash["name"]
            if min > diff:
                min = diff
                second = first
                first = image_hash["name"]
        executor.shutdown()

        # 座標JSON取得
        coordinates = []
        with open(f"map_place/map_place_{select}.json", "rb") as f:
            place = json.load(f)

        result = [first, second]
        image_base64 = []
        for name in result:
            if name is None:
                continue

            with open(f"map_image/{select}/{name}", "rb") as image_file:
                data = base64.b64encode(image_file.read()).decode("utf-8")
                image_base64.append(data)

            #  全体図
            whole_image_name = re.sub("\d", "", first)
            with open(f"map_image/{select}/{whole_image_name}", "rb") as image_file:
                data = base64.b64encode(image_file.read()).decode("utf-8")
                image_base64.append(data)

            # 座標取得
            coordinates.append(list(filter(lambda x: x["name"] == name, place)))
    return JSONResponse(content={"coordinates": coordinates, "image_data": image_base64})
