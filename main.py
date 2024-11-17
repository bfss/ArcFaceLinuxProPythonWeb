# -*- coding: utf-8 -*-
import os
from ctypes import *
from uuid import uuid4
import cv2
from fastapi import FastAPI, UploadFile, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic_settings import BaseSettings, SettingsConfigDict
from asf.asf import ASF
from asf.asf_common import *


# 环境变量
class Config(BaseSettings):
    app_id: str
    sdk_key: str
    active_key: str

    model_config = SettingsConfigDict(env_file=".env")

config = Config()

# 建立上传文件夹
os.makedirs('uploads', exist_ok=True)
# 激活SDK并初始化引擎
asf = ASF("lib")
asf.asf_online_activation(config.app_id, config.sdk_key, config.active_key)
h_engine = asf.asf_init_engine(
    ASF_DetectMode.ASF_DETECT_MODE_IMAGE.value,  # 图片模式
    ASF_OrientPriority.ASF_OP_ALL_OUT.value,     # 全角度检测
    1,                                           # 最多只检测1个人脸
    ASF_FACE_DETECT | ASF_FACERECOGNITION,       # 只进行检测和识别
    ASF_RecModel.ASF_REC_LARGE.value,            # 大模型
)

# 工具函数
def extract_feature(image_name):
    image = cv2.imread(image_name)

    # 传给SDK的图片宽度必须是4的倍数，这里直接切掉图片右侧多余的宽度
    image = image[:, :image.shape[1]-image.shape[1]%4, :]
    height, width, _ = image.shape
    img_data = image.flatten()
    img_data_ctypes = (c_ubyte * len(img_data))(*img_data)

    detected_faces = asf.asf_detect_faces(
        h_engine, 
        width,
        height,
        ASVL_PAF_RGB24_B8G8R8,
        img_data_ctypes
    )

    # 提取检测到的人脸信息
    face_rects = cast(
		detected_faces.faceRect, 
		POINTER(MRECT * detected_faces.faceNum)
	).contents
    face_orients = cast(
		detected_faces.faceOrient,
		POINTER(c_int * detected_faces.faceNum)
    ).contents
    face_data_infos = cast(
		detected_faces.faceDataInfoList,
		POINTER(ASF_FaceDataInfo * detected_faces.faceNum)
    ).contents

    single_detected_face = ASF_SingleFaceInfo()
    single_detected_face.faceRect = face_rects[0]
    single_detected_face.faceOrient = face_orients[0]
    single_detected_face.faceDataInfo = face_data_infos[0]

    feature = asf.asf_face_feature_extract(
        h_engine,
        width,
        height,
        ASVL_PAF_RGB24_B8G8R8,
        img_data_ctypes,
        single_detected_face,
        ASF_RegisterOrNot.ASF_RECOGNITION.value,
        0
    )
    
    return feature


app = FastAPI()
# 设置HTNL模板目录，主要用于演示接口
templates = Jinja2Templates(directory="templates")
# 挂载 static 文件夹到 /static 路径，用来家在本地 bootstrap
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/compare/")
async def compare(
    image_1: UploadFile, 
    image_2: UploadFile
):
    # 读取文件内容
    content_1 = await image_1.read()
    content_2 = await image_2.read()

    image_name_1 = uuid4().hex + '.jpg'
    image_name_2 = uuid4().hex + '.jpg'

    # 这里先保存上传的图片再读取
    with open(f"uploads/{image_name_1}", "wb") as f:
        f.write(content_1)
    with open(f"uploads/{image_name_2}", "wb") as f:
        f.write(content_2)

    try:
        feature_1 = extract_feature(f"uploads/{image_name_1}")
        feature_2 = extract_feature(f"uploads/{image_name_2}")

        confidence_level = asf.asf_face_feature_compare(
            h_engine,
            feature_1,
            feature_2,
            ASF_CompareModel.ASF_LIFE_PHOTO.value
        )
    except:
        raise HTTPException(500, "对比失败")

    return {"confidence_level": confidence_level}

@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html"
    )
