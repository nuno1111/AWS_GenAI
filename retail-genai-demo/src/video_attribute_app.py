import streamlit as st
import src.video_attribute_lib as glib

# st.set_page_config(layout="wide", page_title="홈쇼핑 속성 추출")

frame_prompt = """해당 이미지는 홈쇼핑 방송에서 한 frame을 캡처한 것입니다.

- 이미지 우측에 제품명/가격/카드 정보가 있는 네모 박스가 있나요? 네모 박스의 존재 여부는 <right_box> 태그에 Y/N으로 표현됩니다.
- 'right_box' 값이 'Y'이라면 네모박스에서 "대표상품명/가격/행사카드할인율"을 추출하고, right_box' 값이 'N'이라면 전체화면에서 "대표상품명/가격/행사카드할인율"을 추출해주세요.

<가격유의사항>
- 가격부분을 특히 유의해주세요. 기본가격이 있고, [앱할인가] or [행카카드할인율] 이 적용한 가격이 표현될 수 있습니다.
  - 예를 들어 원래 가격이 "1,000,000원" 인 경우, 
  - 앱할인 "50,000원"이 적용되면 "1,000,000 - 50,000 = 950,000원" 입니다.
  - 앱할인에 추가로 행사카드 10%가 적용되면 "950,000 x 0.9 = 855,000원" 이 표시될수 있습니다.
  - 반드시 원래가격인 "1,000,000원"이 표시되어야 합니다.
  - 앱할인정보와 행사카드할인정보는 같이 표시 될수 있습니다. "앱 x만원 + 행사카드 x%" 라고 표시되어 있으면, "앱할인정보"가 "앱할인 x만원" 이고, "행사카드할인율"이 "행사카드 x% 할인" 이 됩니다.
</가격유의사항>

- 추출해야 될 속성명은 다음과 같습니다.
  1. 대표상품명 : 해당상품명을 추출해주세요. 우측네모박스가 있다면 네모박스 가장 상단에 대표상품명이 위치합니다.
  2. 가격 : 가격은 선택 옵션으로 2개 이상이 될 수 있습니다. 2개 이상일 경우 "선택1", "선택2" 이렇게 표시가 있습니다. 선택사항이 있을수 있으니, 가격이 한개라도 복수개로 표현해주세요. ex) json 표현으로 [] 
    2.1 : 선택명 - 선택옵션을 구분하는 이름, '선택1 [선택명]' 이렇게 표현되어 있습니다.  ex) 선택1 xx 박스
    2.2 : 가격 - 숫자 + 통화로 표현해주세요. 위 <가격유의사항>을 유의하여 앱할인,행사카드할인 적용이 되지 않은 원가격을 표시해주세요. ex) xx,xxx 원
    2.3 : 무이자개월수 - 할부시 무이자가능한 개월수, '무12'는 무이자 12개월을, '무6'로 표현되어 있으면 무이자 6개월을 뜻합니다. 반드시 '무x' 형식으로 알려주세요. ex) 무3, 무6 or 무12
    2.4 : 앱할인가 - 앱으로 구매시 추가 할인 가격 or 추가 할인율을 말합니다. - '앱할인 5만원시' or '앱주문 5만원 할인' or '앱할인율 10 %' 이런 문구가 있으면 '앱할인 5만원' 라고 알려주세요. ex) 앱할인 x만원
    2.5 : 최종 월납부금 - 2.1 ~ 2.4를 모두 적용하여, 무이자기간동안 한달에 내는 금액입니다. '월 xx,xxx원' 이렇게 많이 표현이 됩니다. ex) 월 xx,xxx원
  3. 행사카드할인율 - 해당 제품의 특별 행사기간에 특정 카드 이용시 추가 할인이 가능한 정보입니다. '행사카드 5% 할인시' 이렇게 표현이 되어 있다면 '행사카드 5% 할인' 라고 알려주세요. ex) '행사카드 x% 할인'

- 추출할 수 있는 값이 없다면 "없음"으로 표현해주세요.

- 결과값의 예시는 다음과 같습니다.
<result>
    <right_box>Y<right_box>
    <result_json>
{
    "대표상품명": "소엽렴 콘드로이친 1200",
    "가격":
    [
        {
            "선택명": "선택1 xxxx",
            "가격": "xxx,000원",
            "무이자개월수": 무xx,
            "앱할인가": "앱할인 x만원",
            "최종 월납부금": "월 xx,xxx원"
        },
        {
            "선택명": "선택2 xxxx", 
            "가격": "xxx,000원",
            "무이자개월수": 무xx,
            "앱할인가": "앱할인 x만원",
            "최종 월납부금": "월 xx,xxx원"
        }
    ],
    "행사카드할인율": "행사카드 x% 할인"
}
    </result_json>
</result>
"""

system_prompt = """<instruction>
- 답변결과는 다음과 <result> 태그 예시와 같이 출력해주세요.
- <result> 태그 앞뒤에 부가 설명없이 반드시 <result> 태그만 결과로 알려주세요.
</instruction>

<result>
{
    "대표상품명": "[대표상품명]",
    "가격":
    [
        {
            "선택명": "[선택명]",
            "가격": "[가격]",
            "무이자개월수": [무이자개월수],
            "앱할인가": "[앱할인가]"
        },
        {
            "선택명": "[선택명]",
            "가격": "[가격]",
            "무이자개월수": [무이자개월수],
            "앱할인가": "[앱할인가]"
        }
    ],
    "행사카드할인율": "[행사카드 x% 할인]"
}
</result>
"""

final_prompt = """<input_text_list/>

<instruction>
- <input_text_list> 태그 값은 홈쇼핑 동영상내 여러 frame으로부터 "대표상품명/가격/행사카드할인율" 정보를 추출한 text이고, Hallucinations이 있을 수 있습니다.
- 여러 frame에 나오는 반복해서 값이 있는 항목은 빈도수를 확률적으로 고려하여 대표값을 추출해주세요. 
- 여러 frame에 대부분 "없음"으로 나오는 항목은 "없음"은 무시하고, 최대한 값이 있는 데이터를 추출해주세요.
</instruction>

<가격유의사항>
- 가격부분을 특히 유의해주세요. 기본가격이 있고, [앱할인가] or [행카카드할인율] 이 적용한 가격이 표현될 수 있습니다.
  - 예를 들어 원래 가격이 "1,000,000원" 인 경우, 
  - 앱할인 "50,000원"이 적용되면 "1,000,000 - 50,000 = 950,000원" 입니다.
  - 앱할인에 추가로 행사카드 10%가 적용되면 "950,000 x 0.9 = 855,000원" 이 표시될수 있습니다.
  - 반드시 원래가격인 "1,000,000원"이 표시되어야 합니다.
  - 앱할인정보와 행사카드할인정보는 같이 표시 될수 있습니다. "앱 x만원 + 행사카드 x%" 라고 표시되어 있으면, "앱할인정보"가 "앱할인 x만원" 이고, "행사카드할인율"이 "행사카드 x% 할인" 이 됩니다.
</가격유의사항>

- 추출해야 될 속성명은 다음과 같습니다.
  1. 대표상품명 : 해당상품명을 추출해주세요. 우측네모박스가 있다면 네모박스 가장 상단에 대표상품명이 위치합니다.
  2. 가격 : 가격은 선택 옵션으로 2개 이상이 될 수 있습니다. 2개 이상일 경우 "선택1", "선택2" 이렇게 표시가 있습니다. 선택사항이 있을수 있으니, 가격이 한개라도 복수개로 표현해주세요. ex) json 표현으로 [] 
    2.1 : 선택명 - 선택옵션을 구분하는 이름, '선택1 [선택명]' 이렇게 표현되어 있습니다.  ex) 선택1 xx 박스
    2.2 : 가격 - 숫자 + 통화로 표현해주세요. 위 <가격유의사항>을 유의하여 앱할인,행사카드할인 적용이 되지 않은 원가격을 표시해주세요. ex) xx,xxx 원
    2.3 : 무이자개월수 - 할부시 무이자가능한 개월수, '무12'는 무이자 12개월을, '무6'로 표현되어 있으면 무이자 6개월을 뜻합니다. 반드시 '무x' 형식으로 알려주세요. ex) 무3, 무6 or 무12
    2.4 : 앱할인가 - 앱으로 구매시 추가 할인 가격 or 추가 할인율을 말합니다. - '앱할인 5만원시' or '앱주문 5만원 할인' or '앱할인율 10 %' 이런 문구가 있으면 '앱할인 5만원' 라고 알려주세요. '앱할인' 이나 '앱주문' 이라는 문구가 반드시 포함되어야 합니다. ex) 앱할인 x만원
  3. 행사카드할인율 - 해당 제품의 특별 행사기간에 특정 카드 이용시 추가 할인이 가능한 정보입니다. '행사카드 5% 할인시' 이렇게 표현이 되어 있다면 '행사카드 5% 할인' 라고 알려주세요. '행사카드'라는 문구가 반드시 포함되어야 합니다. ex) '행사카드 4% 할인'

- 결과값의 예시는 다음과 같습니다.
<result>
{
    "대표상품명": "[대표상품명]",
    "가격":
    [
        {
            "선택명": "선택1 xx박스",
            "가격": "xxx,000원",
            "무이자개월수": xx,
            "앱할인가": "앱할인 x만원"
        },
        {
            "선택명": "선택2 xx박스", 
            "가격": "xxx,000원",
            "무이자개월수": x,
            "앱할인가": "앱할인 x만원",
        }
    ],
    "행사카드할인율": "행사카드 x% 할인"
}
</result>
"""
def video_attribute_app_main():
    st.title("방송 속성 추출")

    col1, col2, col3 = st.columns(3)

    video_options_dict = {
        "소연골_콘드로이친_1200": "data/video/TC00093255.mp4",
        # "일반식품_김동완 갈비_LB": "data/video/0131_1735_일반식품_김동완 갈비_LB.mp4",
        "코데즈컴바인_에어윈드_BB브라세트": "data/video/TC00093264.mp4",
        "제니하우스_염색제_12통": "data/video/TC00093232.mp4",
        "덴프스_트루바이타민X": "data/video/TC00093230.mp4",
        "브루마스_제니_스니커즈": "data/video/TC00083819.mp4"
    }

    video_options = list(video_options_dict)
    input_text_list = None
    total_time = None
    with col1:
        # st.subheader("Frame Prompt")
        with st.expander("Frame_Prompt", expanded=False):

            frame_prompt_text = st.text_area("Frame_Prompt",
                #value=,
                value=frame_prompt,
                height=300,
                label_visibility="collapsed"
            )
        
        # st.subheader("System Prompt")
        with st.expander("System_Prompt", expanded=False):
            system_prompt_text = st.text_area("System_Prompt",
                #value=,
                value=system_prompt,
                height=300,
                label_visibility="collapsed"
            )
        
        # st.subheader("Final Prompt")
        with st.expander("Final_Prompt", expanded=False):
            final_prompt_text = st.text_area("Final_Prompt",
                #value=,
                value=final_prompt,
                height=300,
                label_visibility="collapsed"
            )
        go_button = st.button("Go", type="primary")

        # st.subheader("분석정보")
        target_min = st.number_input("분석 분량을 선택해주세요(분)", min_value=1, max_value=60, step=1, value=3)
        cycle_sec = st.number_input("Frame 추출 주기를 선택해주세요(초)", min_value=4, max_value=60, step=1, value=10)
        
        # st.subheader("방송선택")
        
        video_selection = st.radio("방송선택:", video_options)
        
        st.video(video_options_dict[video_selection]) 

    with col2:
        st.subheader("Frame 분석 결과")
        if go_button:
            with st.spinner("Processing..."):
                video_file = video_options_dict[video_selection]
                # glib.get_input_text(video_file, target_min, cycle_sec, frame_prompt_text)
                input_text_list, execution_time = glib.get_input_text(video_file, target_min, cycle_sec, frame_prompt_text)

    with col3:
        st.subheader("최종 분석 결과")
        if input_text_list:
            with st.spinner("Processing..."):
                glib.get_final_result(input_text_list, system_prompt_text, final_prompt_text, execution_time)