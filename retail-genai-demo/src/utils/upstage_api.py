import requests
 
## 개인 Key 입니다. Freetier 완료 후 사용 안됩니다.
api_key = "[your_key]" 
url = "https://api.upstage.ai/v1/document-ai/ocr"
headers = {"Authorization": f"Bearer {api_key}"}

def get_ocr(input_image_base64):
    files = {"document": input_image_base64}
    response = requests.post(url, headers=headers, files=files)
    
    # print("--------------------------")
    # print(response)
    # print("--------------------------")
    
    return response.json()["text"]
