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

def get_input_text(video_file, target_min, cycle_sec, frame_prompt_text):
    # print("target_min => ", target_min, ", cycle_sec => ", cycle_sec)
    # 시작 시간 기록
    start_time = time.time()

    # VideoFileClip 객체 생성
    video = VideoFileClip(video_file)
    frames = [video.get_frame(t) for t in range(0, int(target_min * 60), cycle_sec)]

    input_text_list = ""

    for i, frame in enumerate(frames):
        img = Image.fromarray(frame)
        
        ## 우측 가격정보 crop 추가 
        cropped_img = img.crop((990, 150, 1230, 640))

        st.image(cropped_img)

        crop_byte_stream = io.BytesIO()
        cropped_img.save(crop_byte_stream, format='JPEG')  # 이미지 형식을 지정합니다. (예: PNG, JPEG 등)
        ocr_text = upstage_api.get_ocr(crop_byte_stream.getvalue())
        st.write("Frame ", i, " ocr_text => ", ocr_text)
        
        crop_byte_stream.seek(0)
        input_image_base64 = base64.b64encode(crop_byte_stream.getvalue()).decode('utf-8')
        
        # frame_file = f"{output_folder}/frame_{i}.png"
        # img.save(frame_file)
        # st.write("frame " + str(i) + " : ")
        
        # 이미지를 바이트 스트림으로 변환
        # byte_stream = io.BytesIO()
        # img.save(byte_stream, format='JPEG')  # 이미지 형식을 지정합니다. (예: PNG, JPEG 등)
        # byte_stream.seek(0)

        # 바이트 스트림을 base64로 인코딩
        # input_image_base64 = base64.b64encode(byte_stream.getvalue()).decode('utf-8')
        
        body = json.dumps(
            { 
                "anthropic_version":"bedrock-2023-05-31",
                "max_tokens": 4096,
                "temperature": 0.0,
                # "system": system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg", 
                                    "data": input_image_base64,
                                },
                            },
                            {
                                "type": "text",
                                "text": frame_prompt_text.replace(
                                "<ocr_text/>",
                                """<ocr_text>"""+ocr_text+"""</ocr_text>"""
                            )
                            }
                        ],
                    }
                ]
            }    
        )
        
        response = bedrock_rt.invoke_model(body=body, modelId=sonnet_modelId)

        response_body = json.loads(response.get('body').read())
        output = response_body['content'][0]['text']
        st.write("Frame ", i, " output => ", output)

        # container_text.empty()
        # container_text.write("Frame ", i, " => ", output )
        # container = st.container()

        # with container:
        #     st.image(img)
        #     st.write("Frame ", i, " => ", output)
        
        input_text_list = input_text_list + "Frame " + str(i) + " => " + output + "\n\n"
    
    # 종료 시간 기록
    end_time = time.time()

    # 수행 시간 계산 및 출력
    execution_time = end_time - start_time
    # total_time = f"수행 시간: {execution_time:.6f} 초"
    # print(total_time)
    
    return input_text_list, execution_time

def get_final_result(input_text, system_prompt, final_prompt, execution_time):
    start_time = time.time()

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
                                "<input_text_list/>",
                                """<input_text_list>"""+input_text+"""</input_text_list>"""
                            )
                        }
                    ],
                }
            ]
        }    
    )

    response = bedrock_rt.invoke_model(body=body, modelId=sonnet_modelId)

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

    # print(json_text)
    # JSON 데이터로 파싱
    data = json.loads(json_text)
    
    end_time = time.time()
    # 수행 시간 계산 및 출력
    total_time = execution_time + end_time - start_time
    total_time_text = f"수행 시간: {total_time:.6f} 초"
    
    # JSON 데이터 출력
    st.write(total_time_text)
    st.json(data)
    
