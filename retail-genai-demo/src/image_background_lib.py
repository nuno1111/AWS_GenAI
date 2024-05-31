import os
import boto3
import json
import base64
from io import BytesIO
from random import randint


def get_file_bytes(image):
    byte_stream = BytesIO()
    image.save(byte_stream, format='PNG')
    file_bytes = byte_stream.getvalue()
    return file_bytes

#파일 바이트에서 BytesIO 객체 가져오기
def get_bytesio_from_bytes(image_bytes):
    image_io = BytesIO(image_bytes)
    return image_io


#파일 바이트에서 base64로 인코딩된 문자열 가져오기
def get_base64_from_bytes(image_bytes):
    resized_io = get_bytesio_from_bytes(image_bytes)
    img_str = base64.b64encode(resized_io.getvalue()).decode("utf-8")
    return img_str


#디스크의 파일에서 바이트 로드
def get_bytes_from_file(file_path):
    with open(file_path, "rb") as image_file:
        file_bytes = image_file.read()
    return file_bytes



#InvokeModel API 호출에 대한 문자열화된 리퀘스트 바디를 가져옵니다.
def get_titan_image_background_replacement_request_body(prompt, image_bytes, mask_prompt, negative_prompt=None, outpainting_mode="DEFAULT"):
    
    input_image_base64 = get_base64_from_bytes(image_bytes)

    body = { #InvokeModel API에 전달할 JSON 페이로드를 생성합니다.
        "taskType": "OUTPAINTING",
        "outPaintingParams": {
            "image": input_image_base64,
            "text": prompt,  # 생성할 배경에 대한 설명
            "maskPrompt": mask_prompt,  # 유지해야 할 요소
            "outPaintingMode": outpainting_mode,  # "DEFAULT"는 마스크를 부드럽게 합니다. "PRECISE"는 선명하게 유지합니다.
        },
        "imageGenerationConfig": {
            "numberOfImages": 1,  # 생성할 변형 개수
            "quality": "premium",  # 허용되는 값은 " standard" 또는 "premium"입니다.
            "height": 1408,
            "width": 768,
            "cfgScale": 8.0,
            "seed": randint(0, 100000),  # 랜덤 시드 사용
        },
    }
    
    if negative_prompt:
        body['outPaintingParams']['negativeText'] = negative_prompt
    
    return json.dumps(body)



#Titan Image Generator 응답에서 BytesIO 객체를 가져옵니다.
def get_titan_response_image(response):

    response = json.loads(response.get('body').read())
    
    images = response.get('images')
    
    image_data = base64.b64decode(images[0])

    return BytesIO(image_data)


#Amazon Titan Image Generator를 사용하여 이미지 생성
def get_image_from_model(prompt_content, image_bytes, mask_prompt=None, negative_prompt=None, outpainting_mode="DEFAULT"):
    session = boto3.Session(
        profile_name=os.environ.get("BWB_PROFILE_NAME")
    ) #AWS 자격 증명에 사용할 프로필 이름 설정
    
    bedrock = session.client(
        service_name='bedrock-runtime', #Bedrock 클라이언트를 생성
        region_name=os.environ.get("BWB_REGION_NAME"),
        endpoint_url=os.environ.get("BWB_ENDPOINT_URL")
    ) 
    
    body = get_titan_image_background_replacement_request_body(prompt_content, image_bytes, mask_prompt=mask_prompt, negative_prompt=negative_prompt, outpainting_mode=outpainting_mode) #mask prompt "objects to keep" prompt text "description of background to add"
    
    response = bedrock.invoke_model(body=body, modelId="amazon.titan-image-generator-v1", contentType="application/json", accept="application/json")
    
    output = get_titan_response_image(response)
    
    return output

