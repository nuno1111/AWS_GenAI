import os
import json
from json import JSONDecodeError
# from langchain.llms.bedrock import Bedrock
from langchain_community.chat_models import BedrockChat

def get_llm():

    llm = BedrockChat( #create a Bedrock llm client
        credentials_profile_name=os.environ.get("BWB_PROFILE_NAME"), #AWS 자격 증명에 사용할 프로필 이름을 설정합니다(기본값이 아닌 경우).
        region_name=os.environ.get("BWB_REGION_NAME"), #리전 이름을 설정합니다(기본값이 아닌 경우).
        endpoint_url=os.environ.get("BWB_ENDPOINT_URL"), #엔드포인트 URL을 설정합니다(필요한 경우).

        # model_id="anthropic.claude-v2:1", #Anthropic Claud-v2 모델
        # model_kwargs = {"max_tokens_to_sample": 2048, "temperature": 0.5 } #데이터 추출을 위해서는 temperature가 낮은 것이 가장 좋습니다.

        model_id="anthropic.claude-3-haiku-20240307-v1:0",
        model_kwargs = {"max_tokens": 2048, "temperature": 0.5 } #데이터 추출을 위해서는 temperature가 낮은 것이 가장 좋습니다.

        #model_id="ai21.j2-ultra-v1", #use the AI21 Jurassic-2 Ultra model
        #model_kwargs = {"maxTokens": 1024, "temperature": 0.0 } #for data extraction, minimum temperature is best

    
    )

    return llm

def validate_and_return_json(response_text):
    try:
        response_json = json.loads(response_text) #텍스트를 JSON으로 로드하려고 시도합니다.
        return False, response_json, None #has_error, response_content, err을 반환합니다.
    
    except JSONDecodeError as err:
        return True, response_text, err #has_error, response_content, err을 반환합니다.

def get_json_response(input_content): #text-to-text client 함수
    
    llm = get_llm()

    response = llm.predict(input_content) #프롬프트에 대한 텍스트 응답
    
    return validate_and_return_json(response)

def get_llm_response(input_content): #text-to-text client 함수
    
    llm = get_llm()

    response = llm.predict(input_content) #프롬프트에 대한 텍스트 응답
    
    return response