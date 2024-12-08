# -*- coding: utf-8 -*-
"""特征提取工具"""
from ctypes import *
import cv2
from asf.asf_common import *


def extract_feature(image_name, asf, h_engine):
    """提取人脸特征"""
    # 读取图片
    image = cv2.imread(image_name)

    # 传给SDK的图片宽度必须是4的倍数，这里向外扩大到符合比例要求的宽度
    # 获取图片的高度和宽度
    height, width = image.shape[:2]

    # 计算需要补齐的宽度像素列数，确保列数在0到3的范围内
    padding = (4 - (width % 4)) % 4

    # 在右侧补齐宽度
    image = cv2.copyMakeBorder(
        image, 
        top=0, 
        bottom=0, 
        left=0, 
        right=padding, 
        borderType=cv2.BORDER_CONSTANT, 
        value=[0, 0, 0]  # 宽度用黑色填充
    )

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
