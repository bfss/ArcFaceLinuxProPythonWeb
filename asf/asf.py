# -*- coding: utf-8 -*-
"""SDK Python封装"""
import os
from ctypes import *
from asf.asf_common import *


class ASF():
    def __init__(self, sdk_path):
        # 先加载依赖库避免OS Error
        self._ = CDLL(os.path.join(sdk_path, 'libarcsoft_face.so'))
        # 加载引擎库
        self.sdk = CDLL(os.path.join(sdk_path, 'libarcsoft_face_engine.so'))

    def asf_online_activation(self, app_id, sdk_key, activte_key):
        """在线激活"""
        self.sdk.ASFOnlineActivation.argtypes = [
            c_char_p, # [in] APPID 官网下载
            c_char_p, # [in] SDKKEY 官网下载
            c_char_p  # [in] ActiveKey 官网下载
        ]
        self.sdk.ASFOnlineActivation.restype = c_long

        result = self.sdk.ASFOnlineActivation(
            app_id.encode('utf-8'),
            sdk_key.encode("utf-8"),
            activte_key.encode('utf-8')
        )
        
        if result != MOK and result != MERR_ASF_ALREADY_ACTIVATED:
            raise Exception(f"激活失败: {result}")
    
    def asf_init_engine(
        self,
        detect_mode,
        detect_face_orient_priority,
        detect_face_max_num,
        combined_mask,
        rec_model
    ):
        """引擎初始化"""
        self.sdk.ASFInitEngine.argtypes = [
            c_int,            # [in] AF_DETECT_MODE_VIDEO 视频模式：适用于摄像头预览，视频文件识别
							  #		 AF_DETECT_MODE_IMAGE 图片模式：适用于静态图片的识别
            c_int,            # [in] 检测脸部的角度优先值，参考 ASF_OrientPriority
            c_int,            # [in] 最大需要检测的人脸个数
            c_int,            # [in] 用户选择需要检测的功能组合，可单个或多个
            c_int,            # [in] 用户选择需要的人脸识别模型
            POINTER(c_void_p) # [out] 初始化返回的引擎handle
        ]
        self.sdk.ASFInitEngine.restype = c_long

        h_engine = c_void_p()
        result = self.sdk.ASFInitEngine(
            detect_mode,
            detect_face_orient_priority,
            detect_face_max_num,
            combined_mask,
            rec_model,
            byref(h_engine)
        )
        
        if result == MOK:
            return h_engine
        else:
            raise Exception(f"初始化失败: {result}")
    
    def asf_detect_faces(
        self,
        h_engine,
        width,
        height,
        color_format,
        img_data,
        detect_model = ASF_DetectModel.ASF_DETECT_MODEL_RGB.value
    ):
        """检测人脸信息"""
        self.sdk.ASFDetectFaces.argtypes = [
            c_void_p,                   # [in] 引擎handle
            c_int,                      # [in] 图片宽度
            c_int,                      # [in] 图片高度
	        c_int,                      # [in] 颜色空间格式
	        POINTER(c_ubyte),           # [in] 图片数据
	        POINTER(ASF_MultiFaceInfo), # [out] 检测到的人脸信息 
	        c_int                       # [in] 预留字段，当前版本使用默认参数即可
        ]
        self.sdk.ASFDetectFaces.restype = c_long

        detected_faces = ASF_MultiFaceInfo()
        result = self.sdk.ASFDetectFaces(
            h_engine,
            width,
            height,
            color_format,
            img_data,
            detected_faces,
            detect_model
        )

        if result == MOK:
            return detected_faces
        else:
            raise Exception(f'检测失败: {result}')

    def asf_face_feature_extract(
        self,
        h_engine,
        width,
        height,
        color_format,
        img_data,
        single_face_info,
        register_or_not,
        mask
    ):
        """单人脸特征提取"""
        self.sdk.ASFFaceFeatureExtract.argtypes = [
	        c_void_p,                     # [in] 引擎handle
	        c_int,                        # [in] 图片宽度
	        c_int,                        # [in] 图片高度
	        c_int,                        # [in] 颜色空间格式
	        POINTER(c_ubyte),             # [in] 图片数据
	        POINTER(ASF_SingleFaceInfo),  # [in] 单张人脸位置和角度信息
	        c_int,                        # [in] 注册 1 识别为 0
	        c_int,                        # [in] 带口罩 1，否则0
	        POINTER(ASF_FaceFeature)      # [out] 人脸特征
        ]
        self.sdk.ASFFaceFeatureExtract.restype = c_long
        
        face_feature = ASF_FaceFeature()
        result = self.sdk.ASFFaceFeatureExtract(
            h_engine,
            width,
            height,
            color_format,
            img_data,
            byref(single_face_info),
            register_or_not,
	        mask,
	        byref(face_feature)
        )

        def copy_face_feature(face_feature):
            # 创建一个新的 ASF_FaceFeature 结构体
            face_feature_copy = ASF_FaceFeature()

            # 复制 featureSize
            face_feature_copy.featureSize = face_feature.featureSize

            # 复制 feature 数据
            # 先创建一个新的 ctypes 数组来存储 feature 数据
            face_feature_copy.feature = (c_ubyte * face_feature.featureSize)()
            memmove(face_feature_copy.feature, face_feature.feature, face_feature.featureSize)

            return face_feature_copy
        
        if result == MOK:
            return copy_face_feature(face_feature)
        else:
            raise Exception(f'提取失败: {result}')
        
    def asf_face_feature_compare(
        self,
        h_engine,
        face_feature_1,
        face_feature_2,
        compare_model
    ):
        """人脸特征对比"""
        self.sdk.ASFFaceFeatureCompare.argtypes = [
	        c_void_p,                     # [in] 引擎handle
	        POINTER(ASF_FaceFeature),     # [in] 待比较人脸特征1
	        POINTER(ASF_FaceFeature),     # [in] 待比较人脸特征2
	        POINTER(c_float),             # [out] 比较结果，置信度数值
	        c_int,                        # [in] ASF_LIFE_PHOTO：用于生活照之间的特征比对
										  #      ASF_ID_PHOTO：用于证件照或证件照和生活照之间的特征比对
        ]
        self.sdk.ASFFaceFeatureCompare.restype = c_long

        confidence_level = c_float()
        result = self.sdk.ASFFaceFeatureCompare(
	        h_engine,
	        byref(face_feature_1),
	        byref(face_feature_2),
	        byref(confidence_level),
	        compare_model
        )
        
        if result == MOK:
            return confidence_level.value
        else:
            raise Exception(f'对比失败: {result}')
