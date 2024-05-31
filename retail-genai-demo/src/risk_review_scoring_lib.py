import boto3
import json

#InvokeModel API 호출에 대한 문자열화된 요청 본문 가져오기
def get_text_request_body(prompt, mask_prompt=None, negative_prompt=None):    
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "temperature": 0,
        "messages": [
            {
                "role": "user",
                "content": [
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
def get_response_from_model(prompt_content, model_id, mask_prompt=None):
    session = boto3.Session()
    
    bedrock = session.client(service_name='bedrock-runtime') #Bedrock 클라이언트를 생성합니다
    
    body = get_text_request_body(prompt_content, mask_prompt=mask_prompt)
    
    # modelId = "anthropic.claude-3-haiku-20240307-v1:0"
    
    response = bedrock.invoke_model(body=body, modelId=model_id, contentType="application/json", accept="application/json")
    
    response_body = json.loads(response.get('body').read()) #응답을 읽습니다
    
    output = response_body['content'][0]['text']
    
    return output

