# Host YOLOv5 using SM Endpoint

---

## Blog Description
YOLOv5* model is a popular object detection model known for its runtime efficiency as well as detection accuracy. Many object detection applications use pre-trained YOLOv5 models and are finetuned to detect objects of interest. After data scientists come up with a satisfying model, the model must be deployed to be easily accessible for inference by other members of the organization. Serving a model on Amazon SageMaker Endpoints (https://aws.amazon.com/pm/sagemaker/) can alleviate a lot of the pain points around model scalability and inference cost optimization. Here, we will demonstrate how to host a pre-trained YOLOv5 model on SageMaker Endpoints and use AWS Lambda (https://aws.amazon.com/lambda/) functions to invoke these endpoints. 

(*) **_NOTE:_**  YOLOv5 is distributed under the GPLv3 license.

* Clone the YOLOv5 repository and convert the model from PyTorch to TensorFlow SavedModel format:
```
$ git clone https://github.com/ultralytics/yolov5
$ cd yolov5 
$ pip install -r requirements.txt tensorflow-cpu
$ python export.py --weights yolov5s.pt --include saved_model --nms
$ mkdir export && mkdir export/Servo
$ mv yolov5s_saved_model export/Servo/1
```

* Deploy the model on a SageMaker Endpoint:
```
$ tar -czvf model.tar.gz export/
$ python3 source/deploy.py
```

* For further details about Deploying and Testing, checkout the Notebook: `source/Deploy_and_Test.ipynb`

* Build & Run Docker and store the output zip in the current directory under layers:
```
$ pushd docker
$ docker build --tag aws-lambda-layers:latest <PATH/TO/Dockerfile>
$ docker run -rm -it -v $(pwd):/layers aws-lambda-layers cp /packages/cv2-python37.zip /layers
$ popd
```

* Now we can upload the OpenCV layer artifacts to Amazon S3 and create the Lambda layer:
```
$ aws s3 cp layers/cv2-python37.zip s3://<BUCKET>/<PATH/TO/STORE/ARTIFACTS>
$ aws lambda publish-layer-version --layer-name cv2 --description "Open CV" --content S3Bucket=<BUCKET>,S3Key=<PATH/TO/STORE/ARTIFACTS>/cv2-python37.zip --compatible-runtimes python3.7
```

* Deploy the Lambda function:
```
$ pushd lambda
$ zip app.zip app.py
$ aws s3 cp app.zip s3://<BUCKET>/<PATH/TO/STORE/FUNCTION>
$ aws lambda create-function --function-name yolov5-lambda --handler app.lambda_handler --region us-east-1 --runtime python3.7 --environment "Variables={BUCKET_NAME=$BUCKET_NAME,S3_KEY=$S3_KEY}" --code S3Bucket=<BUCKET>,S3Key="<PATH/TO/STORE/FUNCTION/app.zip>"
$ popd
```

* Once we have the Lambda function and the layer in place, we can connect the layer to the function as follows:
```
$ aws lambda update-function-configuration --function-name yolov5-lambda --layers cv2
```

---

## Contributors:
- [Kevin Song (@kcsong)](https://phonetool.amazon.com/users/kcsong)
- [Romil Shah (@rpshah)](https://phonetool.amazon.com/users/rpshah)