from lib import upstage_api, bedrock

from io import BytesIO



modelId = "anthropic.claude-3-sonnet-20240229-v1:0"
# modelId = "anthropic.claude-3-haiku-20240307-v1:0"


def get_image_analysis(image_bytesIO):
    
    ocr_text = upstage_api.get_ocr(image_bytesIO.getvalue())
    
    prompt_content = """
- 해당 이미지는 Confluence에 Wiki에 첨부된 이미지입니다.
- 해당 이미지의 OCR 정보를 아래 <ocr>태그 안에 추가하였습니다.
- 해당 이미지가 테이블 형식이면 OCR결과를 바탕으로 테이블 형식으로 데이터를 추출해주세요.
- 해당 이미지가 테이블 형식이 아니라면 해당 이미지의 대한 상세한 설명을 추출해주세요.
- 결과는 Markdown 형식으로 만들어주세요.
<ocr/>
- 한글로 결과를 주세요.
"""

    prompt_content = prompt_content.replace(
        "<ocr/>",
        """<ocr>"""+ocr_text+"""</ocr>"""
    )
    
    result = bedrock.get_response_from_model(prompt_content=prompt_content, bytesio=image_bytesIO, model_id=modelId)

    return result