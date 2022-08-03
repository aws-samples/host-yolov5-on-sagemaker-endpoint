# Host YOLOv5 using SM Endpoint

---

## [Blog Link](https://aws.amazon.com/blogs/machine-learning/scale-yolov5-inference-with-amazon-sagemaker-endpoints-and-aws-lambda/)

## Blog Description:
YOLOv5* model is a popular object detection model known for its runtime efficiency as well as detection accuracy. Many object detection applications use pre-trained YOLOv5 models and are finetuned to detect objects of interest. After data scientists come up with a satisfying model, the model must be deployed to be easily accessible for inference by other members of the organization. Serving a model on Amazon SageMaker Endpoints (https://aws.amazon.com/pm/sagemaker/) can alleviate a lot of the pain points around model scalability and inference cost optimization. Here, we will demonstrate how to host a pre-trained YOLOv5 model on SageMaker Endpoints and use AWS Lambda (https://aws.amazon.com/lambda/) functions to invoke these endpoints. 

- Here we are using Amazon SageMaker Notebook instances to run the Notebooks in the [source/](source/) directory. 
- In order to use the Amazon SageMaker Notebook instances, we are using `ml.c5.xlarge` as instance type.
- The kernel used by the Amazon SageMaker Notebooks is `tensorflow2_p38`.

(*) **_NOTE:_**  YOLOv5 is distributed under the GPLv3 license.

Using the following steps, we can get started from downloading the YOLOv5 model, hosting it on Amazon SageMaker Endpoint, testing it and creating AWS Lambda with OpenCV Layers for running the Endpoint:

1. Download YOLOv5 PyTorch model, convert to `tar.gz` format and host on SageMaker Endpoint (More Details: [source/1_Deploy_Model_to_Endpoint.ipynb](source/1_Deploy_Model_to_Endpoint.ipynb)):
  * Clone the YOLOv5 repository and convert the model from PyTorch to TensorFlow SavedModel format:
  ```
  $ git clone https://github.com/ultralytics/yolov5
  $ cd yolov5 
  $ pip install -r requirements.txt tensorflow-cpu
  $ python export.py --weights yolov5l.pt --include saved_model --nms
  $ mkdir export && mkdir export/Servo
  $ mv yolov5l_saved_model export/Servo/1
  ```

  * Store the model in `tar.gz` format and then upload to Amazon S3:
  ```
  $ tar -czvf model.tar.gz export/
  $ aws s3 cp model.tar.gz "<s3://BUCKET/PATH/model.tar.gz>"
  ```

  * Edit deploy script from `source/deploy.py`:
    - Update the Amazon S3 path of the model:
    ```
    model_data = '<s3://BUCKET/PATH/model.tar.gz>'
    ```
    - Update the role created for SageMaker:
    ```
    role = '<IAM ROLE>'
    ```

  * Deploy the model on a SageMaker Endpoint (or follow instructions in the Notebook):
  ```
  $ python3 source/deploy.py
  ```

2. Testing the Endpoint (More Details: [source/2_Test_Endpoint.ipynb](source/2_Test_Endpoint.ipynb)):
  * Setting the Endpoint name and running the Endpoint:
  ```
  ENDPOINT_NAME = 'yolov5l-demo'
  response = runtime.invoke_endpoint(EndpointName=ENDPOINT_NAME, ContentType='application/json', Body=payload)
  ```

3. Create OpenCV Lambda Layers and deploy AWS Lambda app (More Details: [source/3_Lambda_Setup_and_Deploy.ipynb](source/3_Lambda_Setup_and_Deploy.ipynb)):
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
  * Edit Lambda function from `lambda/app.py`:
    - Update the Amazon S3 Bucket name for image access:
    ```
    BUCKET_NAME = "<NAME OF S3 BUCKET FOR INPUT IMAGE>"
    ```
    - Update the Amazon S3 prefix where the image will be stored:
    ```
    IMAGE_LOCATION = "<S3 PREFIX TO IMAGE>/image.png"
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
