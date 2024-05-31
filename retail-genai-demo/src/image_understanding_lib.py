import boto3
import json
import base64
from io import BytesIO


#파일 바이트에서 BytesIO 객체 가져오기
def get_bytesio_from_bytes(image_bytes):
    image_io = BytesIO(image_bytes)
    return image_io


#파일 바이트에서 base64로 인코딩된 문자열 가져오기
def get_base64_from_bytes(image_bytes):
    resized_io = get_bytesio_from_bytes(image_bytes)
    img_str = base64.b64encode(resized_io.getvalue()).decode("utf-8")
    return img_str


#디스크의 파일에서 바이트 로드하기
def get_bytes_from_file(file_path):
    with open(file_path, "rb") as image_file:
        file_bytes = image_file.read()
    return file_bytes

#InvokeModel API 호출에 대한 문자열화된 요청 본문 가져오기
def get_image_understanding_request_body(prompt, image_bytes=None, mask_prompt=None, negative_prompt=None):
    input_image_base64 = get_base64_from_bytes(image_bytes)
    # print("input_image_base64 = > ",input_image_base64)
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "temperature": 0,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg", # this doesn't seem to matter?
                            "data": input_image_base64,
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ],
            }
        ],
    }
    
    return json.dumps(body)

#Anthropic Claude를 사용하여 응답 생성하기
def get_response_from_model(prompt_content, image_bytes, model_id, mask_prompt=None):
    session = boto3.Session()
    
    bedrock = session.client(service_name='bedrock-runtime') #Bedrock 클라이언트를 생성합니다
    
    body = get_image_understanding_request_body(prompt_content, image_bytes, mask_prompt=mask_prompt)
    
    # modelId = "anthropic.claude-3-haiku-20240307-v1:0"
    
    response = bedrock.invoke_model(body=body, modelId=model_id, contentType="application/json", accept="application/json")
    
    response_body = json.loads(response.get('body').read()) #응답을 읽습니다
    
    output = response_body['content'][0]['text']
    
    return output

