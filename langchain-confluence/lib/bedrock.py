import boto3
import json
import base64
from io import BytesIO


#파일 바이트에서 base64로 인코딩된 문자열 가져오기
def get_base64_from_bytes(bytesio):
    img_str = base64.b64encode(bytesio.getvalue()).decode("utf-8")
    return img_str

#InvokeModel API 호출에 대한 문자열화된 요청 본문 가져오기
def get_image_understanding_request_body(prompt, bytesio=None, system_prompt=None):
    input_image_base64 = get_base64_from_bytes(bytesio)
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
def get_response_from_model(prompt_content, bytesio, model_id, system_prompt=None):
    session = boto3.Session()
    
    bedrock = session.client(service_name='bedrock-runtime') #Bedrock 클라이언트를 생성합니다
    
    body = get_image_understanding_request_body(prompt_content, bytesio, system_prompt=system_prompt)
        
    response = bedrock.invoke_model(body=body, modelId=model_id, contentType="application/json", accept="application/json")
    
    response_body = json.loads(response.get('body').read()) #응답을 읽습니다
    
    output = response_body['content'][0]['text']
    
    return output

