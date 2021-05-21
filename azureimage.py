from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobClient, BlobServiceClient, ContainerClient, __version__
from azure.storage.blob import ContentSettings, ContainerClient
from msrest.authentication import CognitiveServicesCredentials
from array import array
import os
from PIL import Image
import sys
import time
import cv2
import numpy as np
import shutil


## Get working Dir make and make an images dir ##

cwd = os.getcwd()
images_dir = "images"

if os.path.isdir(images_dir) == True:
    print("Directory Found!")
else:
    os.mkdir(images_dir)
    print("Directory Created! This will only happen once!")



## Picture and Upload to Azure ##
def picture_upload():
    cap = cv2.VideoCapture(0)

    cv2.namedWindow('test')

    img_counter = 0


    while(True):
        ret, frame = cap.read()
        if not ret:
            print("failed to grab frame")
            break
        cv2.imshow('test', frame)
        
        k = cv2.waitKey(1)
        if k%256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break

        elif k%256 == 32:
            # Space pressed
            img_name = "opencv_frame_0.jpg".format(img_counter)
            cv2.imwrite(img_name, frame)
            print("Taken")
            img_counter += 1

    ## Move file from /Azure-Project to /Azure-Project/images
    original = r'{}/opencv_frame_0.jpg'.format(cwd)
    target = r'{}/images/opencv_frame_0.jpg'.format(cwd)

    shutil.move(original, target)


    cap.release()
    cv2.destroyAllWindows()
    

first_ans = input("Do you want to run images through Azures Computer Vision Software?[y/n]: ")
        
    
if first_ans == 'y' or first_ans == 'Y':
    
    subKey_testonly = input("Would you like to enter your own Sub Key?(Test Only)[y/n]: ")
    if subKey_testonly == 'y':
        subKey_Input = input("Please enter Computer Vision Subscription Key Here: ")
    else:
        print("Invaild")
        
    endpoint_testonly = input("Would you like to enter your own endpoint?(Test Only)[y/n]: ")
    if endpoint_testonly == 'y':
        endpoint_Input = input("Please Computer Vision Endpoint(URL): ")
    else:
        print("Invaild")
else:
    picture_upload()


## Authenticate
## Authenticate your credentials and creates a client
az_credential = DefaultAzureCredential()
if first_ans == 'y' or first_ans == 'Y':
    computervision_client = ComputerVisionClient(endpoint_Input, CognitiveServicesCredentials(subKey_Input))




## Image Capture ##
if first_ans == 'y' or first_ans == 'Y':
    cap = cv2.VideoCapture(0)

    cv2.namedWindow('test')

    img_counter = 0


    while(True):
        ret, frame = cap.read()
        if not ret:
            print("failed to grab frame")
            break
        cv2.imshow('test', frame)
        
        k = cv2.waitKey(1)
        if k%256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break

        elif k%256 == 32:
            # Space pressed
            img_name = "opencv_frame_0.jpg".format(img_counter)
            cv2.imwrite(img_name, frame)
            print("Taken")
            img_counter += 1

    ## Move file from /Azure-Project to /Azure-Project/images
    original = r'{}/opencv_frame_0.jpg'.format(cwd)
    target = r'{}/images/opencv_frame_0.jpg'.format(cwd)

    shutil.move(original, target)


    cap.release()
    cv2.destroyAllWindows()

image_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
local_image_path = os.path.join(image_folder, "opencv_frame_0.jpg")

## Describe an Image - remote
if first_ans == 'y' or first_ans == 'Y':
    
    print("======= Describe in image - camera image =======")
    local_image_path = os.path.join(image_folder, "opencv_frame_0.jpg")
    local_image = open(local_image_path, "rb")

## Call API

    description_results = computervision_client.describe_image_in_stream(local_image)

## Get the descriptions

    print("Description of remote image: ")
    if (len(description_results.captions) == 0):
        print("No description detected.")
    else:
        for caption in description_results.captions:
            print("'{}' with confidence {:.2f}%".format(caption.text, caption.confidence * 100))

## Detecting Objects
if first_ans == 'y' or first_ans == 'Y':
    
    print("======= Detecting faces =======")
    local_image_path = os.path.join(image_folder, "opencv_frame_0.jpg")
    local_image = open(local_image_path, "rb")

    local_image_features = ["faces"]

## Call API

    detect_faces_local = computervision_client.analyze_image_in_stream(local_image, local_image_features)

## Getting details of faces in the images

    print("Faces in the image: ")
    if len(detect_faces_local.faces) == 0:
        print("No faces detected.")
    else:
        for face in detect_faces_local.faces:
            print("{} of age {} at location {}, {}, {}, {}".format(face.gender, face.age, \
            face.face_rectangle.left, face.face_rectangle.top, \
            face.face_rectangle.left, face.face_rectangle.width, \
            face.face_rectangle.top, face.face_rectangle.height))
    print()

                
                
                ## Uploading Pictures to Azure Cloud ##


## Asking if they would like to upload the photo

    

azure_storage_ans = input("Would you like to upload picture to Azure?[y/n]: ")


if azure_storage_ans == 'y' or azure_storage_ans == 'Y':
    conn_string_Input = input("What is your connection string for your storage account?: ")
    image_container_Input = input("What is the blob container name? (has to be created already): ")
    blob_name_upload = input("What would you like to name it? (Add .jpg or .png): ")
    
    blob_service_client = BlobServiceClient.from_connection_string(conn_str=conn_string_Input)
    
    blob_client = blob_service_client.get_blob_client(container=image_container_Input, blob=blob_name_upload)
    
    os.rename(r'{}/images/opencv_frame_0.jpg'.format(cwd), r'{}/images/'.format(cwd) + blob_name_upload)
    print("Uploading " + blob_name_upload + " to Azure Storage as blob")
    with open(image_folder + "/" + blob_name_upload, "rb") as data:
        blob_client.upload_blob(data)
else:
    print("File is now deleted.")
    

## Deletes Photo after use
if os.path.exists(local_image_path):
    os.remove(local_image_path)
    print("Deleted local file.")
else:
    os.path.exists(image_folder + "/" + blob_name_upload)
    os.remove(image_folder + "/" + blob_name_upload)
    print("File deleted on local machine. Moved to azure storage.")
    
print("**Completed**")