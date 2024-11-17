# -*- coding: utf-8 -*-
"""SDK常量、枚举和结构体定义"""
from ctypes import *
from enum import Enum


# 错误代码
MOK = 0 # 成功

MERR_ASF_BASE = 0x16000							# 人脸比对基础错误类型
MERR_ASF_ACTIVATION_FAIL = MERR_ASF_BASE+1		# SDK激活失败,请打开读写权限
MERR_ASF_ALREADY_ACTIVATED = MERR_ASF_BASE+2	# SDK已激活

# 检测类型
ASF_NONE = 0x00000000	            # 无属性
ASF_FACE_DETECT = 0x00000001	    # 此处detect可以是tracking或者detection两个引擎之一，具体的选择由detect mode 确定
ASF_FACERECOGNITION = 0x00000004	# 人脸特征
ASF_AGE = 0x00000008	            # 年龄
ASF_GENDER = 0x00000010	            # 性别
ASF_LIVENESS = 0x00000080	        # RGB活体
ASF_IMAGEQUALITY = 0x00000200	    # 图像质量检测
ASF_IR_LIVENESS = 0x00000400	    # IR活体
ASF_MASKDETECT = 0x00001000	        # 口罩检测

# 颜色空间
ASVL_PAF_RGB24_B8G8R8 = 0x201


# 枚举
class ASF_DetectMode(Enum):
	"""检测模式"""
	ASF_DETECT_MODE_VIDEO = 0x00000000 # Video模式，一般用于多帧连续检测
	ASF_DETECT_MODE_IMAGE = 0xFFFFFFFF # Image模式，一般用于静态图的单次检测

class ASF_OrientPriority(Enum):
	"""检测时候人脸角度的优先级"""
	ASF_OP_0_ONLY = 0x1     # 常规预览下正方向
	ASF_OP_90_ONLY = 0x2	# 基于0°逆时针旋转90°的方向
	ASF_OP_270_ONLY = 0x3	# 基于0°逆时针旋转270°的方向
	ASF_OP_180_ONLY = 0x4	# 基于0°旋转180°的方向（逆时针、顺时针效果一样）
	ASF_OP_ALL_OUT = 0x5	# 全角度
	
class ASF_RecModel(Enum):
	"""人脸识别可选的模型"""
	ASF_REC_LARGE = 0x1	    # 人脸识别大模型
	ASF_REC_MIDDLE = 0x2    # 人脸识别中模型
	
class ASF_DetectModel(Enum):
	"""检测模型"""
	ASF_DETECT_MODEL_RGB = 0x1	# RGB图像检测模型
	                            # 预留扩展其他检测模型
								
class ASF_RegisterOrNot(Enum):
	ASF_RECOGNITION = 0x0   # 用于识别照人脸特征提取
	ASF_REGISTER = 0x1      # 用于注册照人脸特征提取
	
class ASF_CompareModel(Enum):
	ASF_LIFE_PHOTO = 0x1	# 用于生活照之间的特征比对，推荐阈值0.80
	ASF_ID_PHOTO = 0x2		# 用于证件照或生活照与证件照之间的特征比对，推荐阈值0.82
	

# 结构体
class MRECT(Structure):
	"""人脸框"""
	_fields_ = [
        ("left", c_int),
        ("top", c_int),         
        ("right", c_int),
        ("bottom", c_int)
    ]

class ASF_FaceDataInfo(Structure):
	"""人脸信息"""
	_fields_ = [
		("data", c_void_p), # 人脸信息
		('dataSize', c_int) # 人脸信息长度
    ]
	
class ASF_Face3DAngleInfo(Structure):
	"""3D角度信息"""
	_fields_ = [
		("roll", POINTER(c_float)),
		("yaw", POINTER(c_float)),
		("pitch", POINTER(c_float))
    ]

class ASF_MultiFaceInfo(Structure):
	"""多人脸框信息"""
	_fields_ = [
        ("faceNum", c_int),                              # 检测到的人脸个数
        ("faceRect", POINTER(MRECT)),                    # 人脸框信息
        ("faceOrient", POINTER(c_int)),                  # 人脸图像的角度，可以参考 ASF_OrientCode
        ("faceID", POINTER(c_int)),                      # face ID
        ("faceDataInfoList", POINTER(ASF_FaceDataInfo)), # 人脸检测信息
        ("faceIsWithinBoundary", POINTER(c_int)),        # 人脸是否在边界内 0 人脸溢出；1 人脸在图像边界内
        ("foreheadRect", POINTER(MRECT)),                # 人脸额头区域
        ("face3DAngleInfo", ASF_Face3DAngleInfo)         # 人脸3D角度
    ]

class ASF_SingleFaceInfo(Structure):
	"""单人脸信息"""
	_fields_ = [
		("faceRect", MRECT),                # 人脸框信息
		("faceOrient", c_int),              # 人脸图像角度，可以参考 ASF_OrientCode
		("faceDataInfo", ASF_FaceDataInfo)  # 单张人脸信息
    ]

class ASF_FaceFeature(Structure):
	"""人脸特征信息"""
	_fields_ = [
		("feature", POINTER(c_ubyte)),        # 人脸特征信息
		("featureSize", c_int)                # 人脸特征信息长度 
    ]
