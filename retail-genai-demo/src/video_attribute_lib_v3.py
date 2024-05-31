import streamlit as st
from moviepy.editor import VideoFileClip
from PIL import Image
import boto3
import io
import base64
import json
import time
import re
from src.utils import upstage_api

bedrock_rt = boto3.client("bedrock-runtime")
bedrock = boto3.client("bedrock")

# output_folder = "./output"
sonnet_modelId = "anthropic.claude-3-sonnet-20240229-v1:0"
haiku_modelId = "anthropic.claude-3-haiku-20240307-v1:0"
modelId = sonnet_modelId

## 모든 Frame 분석 결과인 input_text_list 도출
def get_input_ocr_list(video_file, target_min, cycle_sec):
    # print("target_min => ", target_min, ", cycle_sec => ", cycle_sec)
    # 시작 시간 기록
    start_time = time.time()

    # VideoFileClip 객체 생성
    video = VideoFileClip(video_file)
    frames = [video.get_frame(t) for t in range(0, int(target_min * 60), cycle_sec)]

    input_ocr_list = "<input_ocr_list>\n"

    for i, frame in enumerate(frames):
        
        # 원본 이미지를 바이트 스트림으로 변환
        img = Image.fromarray(frame)
        original_byte_stream = io.BytesIO()
        img.save(original_byte_stream, format='JPEG')  # 이미지 형식을 지정합니다. (예: PNG, JPEG 등)
        # original_byte_stream.seek(0)
        # original_image_base64 = base64.b64encode(original_byte_stream.getvalue()).decode('utf-8')
        
        st.image(img)
        original_ocr_text = upstage_api.get_ocr(original_byte_stream.getvalue())
        st.write("Frame " + str(i)," original_ocr =>",original_ocr_text)
        time.sleep(0.5)
             
        ## 우측 가격정보 crop 
        cropped_img = img.crop((990, 150, 1230, 640))
        croped_byte_stream = io.BytesIO()
        cropped_img.save(croped_byte_stream, format='JPEG')  # 이미지 형식을 지정합니다. (예: PNG, JPEG 등)
        # croped_byte_stream.seek(0)
        # croped_image_base64 = base64.b64encode(croped_byte_stream.getvalue()).decode('utf-8')

        ## crop 이미지에서 OCR 정보 추출
        st.image(cropped_img)
        croped_ocr_text = upstage_api.get_ocr(croped_byte_stream.getvalue())
        st.write("Frame " + str(i)," ocr =>",croped_ocr_text)
        time.sleep(0.5)
        # st.write("Frame ", i, " croped_ocr_text => ", croped_ocr_text)
        
        ## OCR만 적용
        input_ocr_list += "<frame>\n"
        input_ocr_list += "  <frame_id>{}</frame_id>\n".format(i)
        input_ocr_list += "  <original_ocr_text>{}</original_ocr_text>\n".format(original_ocr_text)
        input_ocr_list += "  <croped_ocr_text>{}</croped_ocr_text>\n".format(croped_ocr_text)
        input_ocr_list += "</frame>\n"
    input_ocr_list += "</input_ocr_list>"
    
    # 종료 시간 기록
    end_time = time.time()

    # 수행 시간 계산 및 출력
    execution_time = end_time - start_time
    # total_time = f"수행 시간: {execution_time:.6f} 초"
    # print(total_time)
    
    return input_ocr_list, execution_time

def get_final_result(input_ocr_list, system_prompt, final_prompt, execution_time):
    start_time = time.time()

    # st.write(input_ocr_list)

    body = json.dumps(
        { 
            "anthropic_version":"bedrock-2023-05-31",
            "max_tokens": 4096,
            "temperature": 0.0,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": final_prompt.replace(
                                "<input_ocr_list/>",
                                """<input_ocr_list>"""+input_ocr_list+"""</input_ocr_list>"""
                            )
                        }
                    ],
                }
            ]
        }    
    )

    response = bedrock_rt.invoke_model(body=body, modelId=modelId)

    
    print("--------------------------")
    print(response)
    print("--------------------------")
    
    response_body = json.loads(response.get('body').read())
    output = response_body['content'][0]['text']
    
    # print(output)
    
    pattern = r'<result>(.*?)</result>'
    match = re.search(pattern, output, re.DOTALL)
    json_text = match.group(1)
    
    
    # data = json.loads(json_str)
    # print(data)
    # JSON 텍스트에서 <result> 태그 제거
    # json_text = output.replace("<result>", "").replace("</result>", "")

    print(json_text)
    # JSON 데이터로 파싱
    data = json.loads(json_text)
    
    end_time = time.time()
    # 수행 시간 계산 및 출력
    total_time = execution_time + end_time - start_time
    total_time_text = f"수행 시간: {total_time:.6f} 초"
    
    # JSON 데이터 출력
    st.write(total_time_text)
    st.json(data)
    
