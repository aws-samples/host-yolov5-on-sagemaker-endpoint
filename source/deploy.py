import os
import tensorflow as tf
from tensorflow.keras import backend
from sagemaker.tensorflow import TensorFlowModel

model_data = '<s3://BUCKET/PATH/model.tar.gz>'
role = '<IAM ROLE>'

model = TensorFlowModel(model_data=model_data, 
                        framework_version='2.3', role=role)
predictor = model.deploy(initial_instance_count=1, 
                         instance_type='ml.m5.xlarge',
                         endpoint_name='yolov5-demo')
