# ArcFaceLinuxProPythonWeb

此项目对应知乎专栏：[在Python Web项目中集成虹软Linux Pro SDK实现人脸对比API服务](https://zhuanlan.zhihu.com/p/7333724729)

## 项目环境准备

- 在项目根目录新建.env文件，设置从官网获得的激活信息

    > APP_ID = 
    > SDK_KEY = 
    > ACTIVE_KEY = 

- 将SDK中的libarcsoft_face_engine.so和libarcsoft_face.so放到lib目录下

- 如果需要使用HTML Demo，下载并解压bootstrap-5.3.3-dist到static目录下

- 使用pip安装requirements.txt中的依赖（推荐使用虚拟环境）

    > pip install -r requirements.txt

## 项目运行

- 执行uvicorn main:app

- 访问：127.0.0.1:8000
