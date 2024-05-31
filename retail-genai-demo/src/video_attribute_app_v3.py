import streamlit as st
import src.video_attribute_lib_v3 as glib
import tempfile
import os

system_prompt = """<instruction>
- 당신은 홈쇼핑 방송에서 정확한 가격정보를 추출하는 머신입니다.
- 답변결과는 다음과 <result> 태그 예시와 같이 출력해주세요.
- <result> 태그 앞뒤에 부가 설명없이 반드시 <result> 태그만 결과로 알려주세요.
</instruction>

<result>
{
    "대표상품명": "[대표상품명]",
    "가격정보":
    [
        {
            "선택명": "[선택명]",
            "판매가격": "[판매가격]",
            "무이자개월수": "[무이자개월수]",
            "앱할인가": "[앱할인가]",
            "일시불할인가" "[일시불할인가]"
        },
        {
            "선택명": "[선택명]",
            "판매가격": "[판매가격]",
            "무이자개월수": [무이자개월수],
            "앱할인가": "[앱할인가]",
            "일시불할인가" "[일시불할인가]"
        }
    ],
    "행사카드할인율": "[행사카드할인율]",
    "가격행사": ["[특가방송]", "[세일방송]"] 

}
</result>
"""

final_prompt = """<input_ocr_list/>

<instruction>
- <input_ocr_list> 는 홈쇼핑 동영상내 여러 frame으로부터 ocr text 목록이고, Hallucinations이 있을 수 있습니다.
- <input_ocr_list> 으로부터 대표상품명/가격/행사카드할인율/가격행사 정보를 추출해주세요.
</instruction>

<가격정보_유의사항>
 - 가격은 선택옵션으로 2개 이상이 될 수 있습니다. 2개 이상일 경우 "선택1", "선택2" 이렇게 표시가 있는 경우가 많으나 없을수도 있습니다. 
 - 선택사항이 있을수 있으니, 가격이 한개라도 복수개로 표현해주세요. ex) json 표현으로 [] 
 - 가격이 나열되는 순서는 [대표상품명][선택명][판매가격][무이자개월수][앱할인가][일시불할인가] 순으로 많이 나옵니다.
 - 예를 들어 "아마존 영양제 선택1 12박스 279,000 무12 앱할인 5만원시 월 19,084원 선택2 6박스 199,000 무6 앱할인 2만원시 월 29,834원 일시불 7만원 " 이런 OCR은 다음과 같이 정보가 Mapping 됩니다.
    1. 대표상품명 : "아마존 영양제"
    2. 가격
        2.1 선택명 : "선택1 12박스"
        2.2 판매가격 : "279,000"
        2.3 무이자개월수 : "무12"
        2.4 앱할인가 : "앱할인 5만원"
        2.5 일시불할인가 : "일시불 7만원"
</가격정보_유의사항>

<선택명유의사항>
- 선택명은 구매옵션을 구분하는 기준입니다. 절대 사이즈(S/M/L/XL)나 색상을 구분하는 내용은 선택명이 아닙니다.
- 구매옵션이 1개라면 단일상품입니다. 선택명이 없습니다. "선택[숫자]" 이런 형태의 글자가 없다면 선택명은 "없음"으로 표시해주세요.
- '선택[숫자]', '선택[숫자]' 형식인 경우, [숫자]가 작은 순서로 먼저 나와야 합니다.
- '1종', '2종', '1박스', '2박스' 등 '선택'이라는 Text가 없는 형식인 경우, '판매가격'이 비싼 순서로 나열하세요.
</선택명유의사항>

- 추출해야 될 속성명은 다음과 같습니다.
  1. 대표상품명 : 해당상품명을 추출해주세요. OCR 가장 앞이나 가격정보 앞쪽에 대표상품명이 위치합니다.
  2. 가격 : <가격정보_유의사항> 을 참조하여 2.1 선택명부터 2.4판매가격까지 정보를 추출해주세요.
    2.1. 선택명 : <선택명유의사항> 유의하여 선택명을 작성해주세요.
    2.2. 판매가격 : 숫자 + 통화로 표현해주세요. 위 <가격유의사항>을 유의하여 앱할인,행사카드할인 적용이 되지 않은 원가격을 표시해주세요. ex) xx,xxx 원
    2.3. 무이자개월수 : 할부시 무이자가능한 개월수를 '무x' 형식으로 표기합니다. 예를 들어 '무12'는 무이자 12개월을 뜻합니다. 무이자개월수는 가격 정보와 붙어있을 수 있습니다. 예를 들어 '36,900무6'은 가격이 '36,900원'이고 무이자개월수는 '6개월' 입니다. 반드시 '무x' 형식으로 알려주세요. ex) 무3, 무6 or 무12. 무이자개월수는 가격 뒤에 또는 별도로 표기될 수 있습니다. 예를 들어, '89,000 무3' 또는 '89,000원 무3' 또는 '39,000무3' 형식으로 표시됩니다. 가격과 무이자개월수 사이에 공백이 있을 수도, 없을 수도 있습니다.
    2.4. 앱할인가 : 앱으로 구매시 추가 할인 가격 or 추가 할인율을 말합니다. - '앱할인 5만원시' or '앱주문 5만원 할인' or '앱할인율 10 %' 이런 문구가 있으면 '앱할인 5만원' or '앱할인 10%' 라고 알려주세요. ex) 앱할인 x만원, ex) 앱할인 x%
  3. 행사카드할인율 : 해당 제품의 특별 행사기간에 특정 카드 이용시 추가 할인이 가능한 정보입니다. '행사카드 5% 할인시' 이렇게 표현이 되어 있다면 '행사카드 5% 할인' 라고 알려주세요. ex) '행사카드 x% 할인'
  4. 가격행사 : '특가' 또는 '세일' 문구가 있다면 가격행사 대상 방송입니다. '세일'은 영어인 sale, SALE로 표기될 수 있습니다. 이런 문구가 있다면 '특가방송', '세일방송'이라고 알려주세요. 결과값에는 "가격행사" 항목으로 "특가방송" 또는 "세일방송"을 포함한 리스트로 표시해주세요. ex1) '가격행사: ["특가방송"]', ex2)'가격행사: ["세일방송"]', ex3)'가격행사: ["특가방송", "세일방송"]'

- 추출할 수 있는 값이 없다면 "없음"으로 표현해주세요.

- 다음은 추출 되어진 예시입니다.
<example-01>
    <input_ocr_list>
        <frame>
                <frame_id>0</frame_id>
            <ocr>
                아마존 영양제 선택1 12박스 279,000 무12 앱할인 5만원시 월 19,084원 선택2 6박스 199,000 무6 앱할인 2만원시 월 29,834원 앱주문 2만원 할인 행사카드5% 할인 시 170,050무6 월 28,342원
            </ocr>
        </frame>
    </input_ocr_list>
    <result>
    {
        "대표상품명": "아마존 영양제",
        "가격":
        [
            {
                "선택명": "선택1 12박스",
                "판매가격": "279,000원",
                "무이자개월수": 무12,
                "앱할인가": "앱할인 5만원",
                "일시불할인가" "없음"

            },
            {
                "선택명": "선택2 6박스", 
                "가격": "199,000원",
                "무이자개월수": 무6,
                "앱할인가": "앱할인 2만원",
                "일시불할인가" "없음"
            }
        ],
        "행사카드할인율": "행사카드 5% 할인",
        "가격행사": "없음"
    }
    </result>
</example-01>

<example-02>
    <input_ocr_list>
        <frame>
                <frame_id>0</frame_id>
            <ocr>
                아마존 TV 55형 1,580,000무36 월 43,889원 KB국민, 롯데,삼성,신한, 하나,현대 무 36개월/ 그외 카드 무12개월 2024년 3월 출시 최신상
            </ocr>
        </frame>
        <frame>
                <frame_id>1</frame_id>
            <ocr>
                아마존 TV 65형 2,030,000 무36 월 56,389원 KB국민, 롯데, 삼성, 신한, 하나, 현대 무 36개월/ 그외 카드 무 12개월 TV 구매 전고객 GS가 26만9천원 LG 우퍼사운드바 포함 SP2 본품 설치후 2주내 별도배송
            </ocr>
        </frame>
        <frame>
                <frame_id>2</frame_id>
            <ocr>
                아마존 TV 앱 1만원+ 일시불 3만원 행사 카드 5% 할인 시 [55형] 1,463,000원 [65형] 1,890,500원 1인 1일 한도 20만원 특가
            </ocr>
        </frame>
        <frame>
                <frame_id>3</frame_id>
            <ocr>
                아마존 TV 55형 + TV대 1,680,000무36 월 46,666원 KB국민, 롯데,삼성,신한, 하나,현대 무 36개월/ 그외 카드 무12개월 2024년 3월 출시 최신상
            </ocr>
        </frame>
        <frame>
                <frame_id>4</frame_id>
            <ocr>
                아마존 TV 65형 + TV대 2,130,000 무36 월 59,166원 KB국민, 롯데, 삼성, 신한, 하나, 현대 무 36개월/ 그외 카드 무 12개월 TV 구매 전고객 GS가 26만9천원 LG 우퍼사운드바 포함 SP2 본품 설치후 2주내 별도배송
            </ocr>
        </frame>
        <frame>
                <frame_id>5</frame_id>
            <ocr>
                아마존 TV + TV대 앱 1만원+ 일시불 5만원 행사 카드 5% 할인 시 [55형 + TV대] 1,543,000원 [65형 + TV대] 1,570,500원 1인 1일 한도 20만원 특가
            </ocr>
        </frame>
    </input_ocr_list>
    <result>
    {
        "대표상품명": "아마존 TV",
        "가격":
        [
            {
                "선택명": "65형 + TV대", 
                "판매가격": "2,130,000원",
                "무이자개월수": "무36",
                "앱할인가": "앱할인 1만원",
                "일시불할인가": "일시불 5만원"
            },
            {
                "선택명": "65형", 
                "판매가격": "2,030,000원",
                "무이자개월수": "무36",
                "앱할인가": "앱할인 1만원",
                "일시불할인가": "일시불 3만원"
            },
            {
                "선택명": "55형 + TV대",
                "판매가격": "1,680,000원",
                "무이자개월수": "무36",
                "앱할인가": "앱할인 1만원",
                "일시불할인가": "일시불 5만원"
            },
            {
                "선택명": "55형",
                "판매가격": "1,580,000원",
                "무이자개월수": "무36",
                "앱할인가": "앱할인 1만원",
                "일시불할인가": "일시불 3만원"
            }
        ],
        "행사카드할인율": "행사카드 5% 할인",
        "가격행사": ["특가행사"]
    }
    </result>
</example-02>

- 최종 결과값의 Template는 다음과 같습니다.
<result>
{
    "대표상품명": "[대표상품명]",
    "가격정보":
    [
        {
            "선택명": "[선택명]",
            "판매가격": "[판매가격]",
            "무이자개월수": "[무이자개월수]",
            "앱할인가": "[앱할인가]",
            "일시불할인가" "[일시불할인가]"
        },
        {
            "선택명": "[선택명]",
            "판매가격": "[판매가격]",
            "무이자개월수": [무이자개월수],
            "앱할인가": "[앱할인가]",
            "일시불할인가" "[일시불할인가]"
        }
    ],
    "행사카드할인율": "[행사카드할인율]",
    "가격행사": ["[특가방송]", "[세일방송]"] 
}
</result>
"""
def video_attribute_app_main():
    st.title("방송 속성 추출")

    col1, col2, col3 = st.columns(3)

    video_options_dict = {
        "소연골_콘드로이친_1200": "data/video/TC00093255.mp4",
        "코데즈컴바인_에어윈드_BB브라세트": "data/video/TC00093264.mp4",
        "덴프스_트루바이타민X": "data/video/TC00093230.mp4",
        "제니하우스_염색제_12통": "data/video/TC00093232.mp4",
        "브루마스_제니_스니커즈": "data/video/TC00083819.mp4",
        "팔레오_산양유_프로틴_plus_류신_6통": "data/video/TC00093902.mp4",
        "브리엘_가디건_니트원피스": "data/video/TC00090456.mp4",
        "테팔_매직핸즈_화이트_골드_에디션": "data/video/TC00093758.mp4",
        "삼성무풍에어컨": "data/video/TC00093561.mp4",
        "LG_울트라HD_TV": "data/video/TC00092932.mp4",
        "직접_업로드": None
    }

    video_options = list(video_options_dict)
    input_ocr_list = None
    tmp_file_path = None
    with col1:
        
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
        target_min = st.number_input("분석 분량을 선택해주세요(분)", min_value=1, max_value=60, step=1, value=7)
        cycle_sec = st.number_input("Frame 추출 주기를 선택해주세요(초)", min_value=4, max_value=60, step=1, value=10)
        
        # st.subheader("방송선택")
        video_selection = st.radio("방송선택:", video_options)
        if video_selection == "직접_업로드":
            upload_video = st.file_uploader("동영상 업로드", type=["mp4", "avi", "mov"])
            if upload_video is not None:
                # 임시 파일 생성
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
                    tmp_file.write(upload_video.getvalue())
                    tmp_file_path = tmp_file.name
                    
                st.video(tmp_file_path)
                video_file = tmp_file_path
        else:
            video_file = video_options_dict[video_selection]
            st.video(video_options_dict[video_selection]) 
        
        

    with col2:
        st.subheader("Frame 분석 결과")
        if go_button:
            with st.spinner("Processing..."):
                input_ocr_list, execution_time = glib.get_input_ocr_list(video_file, target_min, cycle_sec)

    with col3:
        st.subheader("최종 분석 결과")
        if input_ocr_list:
            with st.spinner("Processing..."):
                glib.get_final_result(input_ocr_list, system_prompt_text, final_prompt_text, execution_time)
                
                if tmp_file_path:
                    os.unlink(tmp_file_path)
                    print("임시파일 삭제 완료")
