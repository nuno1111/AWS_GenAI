import requests
 
## 개인 Key 입니다. Freetier 완료 후 사용 불가능합니다.
## upstage_api.key 파일안에 key를 셋팅해주세요.
with open('./src/utils/upstage_api.key', 'r') as f:
    api_key = f.read().strip()
    
url = "https://api.upstage.ai/v1/document-ai/ocr"
headers = {"Authorization": f"Bearer {api_key}"}

def get_ocr(input_image_base64):
    files = {"document": input_image_base64}
    response = requests.post(url, headers=headers, files=files)
    
    # print("--------------------------")
    # print(response)
    # print("--------------------------")
    
    return response.json()["text"]
