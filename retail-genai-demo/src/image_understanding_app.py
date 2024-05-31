import streamlit as st
import src.image_understanding_lib as glib

def image_understanding_app_main():

    st.title("상품 이미지 분석")

    col1, col2, col3 = st.columns(3)

    image_options_dict = {
        "필립스상품메인": "images/필립스상품메인.png",
        "필립스기능": "images/필립스기능.png",
        "필립스제품스펙": "images/필립스제품스펙.png",
        "필립스AS": "images/필립스AS.png",
        "몽클레어": "images/moncler.jpeg",
        "코드이미지": "images/code_list.png",
        "OCR": "images/ocr.png",
        "Other": "images/house.jpg",
    }

    prompt_options_dict = {
        "상품설명": "상품이미지에 대해서 상세히 설명해주세요.",
        # "Detailed description": "Please provide a thoroughly detailed description of this image.",
        "상품분류": """해당상품의 속성을 분류하여 추출하려고 합니다. 
- 해당 상품에 해당하는 성별은 남성/여성/공용 중 무엇인가요? 
- 내구성은 소비재/내구재 중 무엇인가요?
- 가격은 고가/중가/저가 중 무엇인가요?

답변은 다음과 같이 xml로 만들어 주세요.
<성별>[남성/여성/공용]</성별>
<내구성>[소비재/내구재]</내구성>
<가격>[고가/중가/저가]</가격>
""",
        # "Object recognition": "Please create a comma-separated list of the items found in this image. Only return the list of items.",
        # "Subject identification": "Please name the primary object in the image. Only return the name of the object in <object> tags.",
        # "Writing a story": "Please write a fictional short story based on this image.",
        # "Answering questions": "What emotion are the people in this image displaying?",
        # "Transcribing text": "Please transcribe any text found in this image.",
        # "Translating text": "Please translate the text in this image to French.",
        "제품기능": "상품이미지에서 상품 기능부분을 상세히 추출해주세요.",
        "제품스펙": "상품이미지에서 상품 제품스펙부분을 상세히 추출해주세요.",
        "제품AS": "상품이미지에서 상품 AS부분 특히, 상담시간, 전화번호, 상담채널, 상담방법 등을 상세히 추출해주세요.",
        "몽클레어": """해당상품의 속성을 분류하여 추출하려고 합니다. 
- 해당 상품에 해당하는 성별은 남성/여성/공용 중 무엇인가요? 
- 봄,여름,가을,겨울 중 어느 계절에 해당하는 상품인가요?
- 다음 중 어느 카테고리에 속하나요? 패션의류,패션잡화,스포츠/레저,신성/가공식품,건강식품,뷰티

답변은 다음과 xml로 만들어 주세요.
<성별>[남성/여성/공용]</성별>
<계절>[봄,여름,가을,겨울]</계절>
<카테고리>[패션의류,패션잡화,스포츠/레저,신성/가공식품,건강식품,뷰티]</카테고리>""",
    "코드이미지+OCR 분석 " : """- 첨부된 이미지는 '배송 상태 코드 테이블'에 대한 이미지입니다. 
- 해당 이미지의 OCR 정보를 아래 <ocr>태그 안에 추가하였습니다.
- 가장 먼저, OCR 결과를 기반으로 테이블 형식으로 데이터를 추출해주세요. 
- 위 추출된 테이블 형식 데이터를 근기로 다음 질문에 답해주세요.

<질문>
코드 '22'에 값은 무엇인가요?
</질문>    

<ocr>
CDCNTNT CMMCD CDVAL

1 Sales 22 일반

2 Sales 23 오늘도착

3 Calos 90 S.VID

4 Calor 91 배송불필요:수거지시 후 반품취소

5 Sales 93 맞교환 주문

6 Sales 97 배송불필요

7 Sales 9H 도착일 선택

8 Sales AN 식품당일배송

9 Sales 95 재고범위내 출하

10 Sales QT 선출

11 Sales QY 요우커지정밀

12 Sales QZ 요우커일반

13 Return 01 수거필요

14 Return 02 수거불필요:택배사분실

15 Return 03 수거불필요:택배사분실

16 Return 04 수거불필요.업체입고료건

17 Return 05 수거불필요:카드도용고객

18 Return 06 수거불필요:AS불가

19 Return 07 수거불필요:가주문번품건

20 Return 08 수거불필요:기타

21 Return 09 맞교환 반품

22 Return OA 수거불필요:고객직접발송

23 Return 10 반품취소

24 Return 11 수취거절:배송전 취소

25 Return 12 수거지정일

26 Return 13 편의점반품

27 Return 14 수거불필요:편의점분실

28 Return 92 수거불필요:수거지시후반품취소
<ocr>

    """,
    "Other": "",
    }

    image_options = list(image_options_dict)
    prompt_options = list(prompt_options_dict)
    with col1:
        st.subheader("Select an Image")
        
        image_selection = st.radio("Image example:", image_options)
        
        if image_selection == 'Other':
            uploaded_file = st.file_uploader("Select an image", type=['png', 'jpg'], label_visibility="collapsed")
        else:
            uploaded_file = None
        
        if uploaded_file and image_selection == 'Other':
            uploaded_image_preview = glib.get_bytesio_from_bytes(uploaded_file.getvalue())
            st.image(uploaded_image_preview)
        else:
            st.image(image_options_dict[image_selection])
        
        
    with col2:
        st.subheader("Prompt")
        
        model_options_dict = {
            "claude 3 - haiku": "anthropic.claude-3-haiku-20240307-v1:0",
            "claude 3 - sonnet": "anthropic.claude-3-sonnet-20240229-v1:0",
        }

        model_options = list(model_options_dict)
        model_selection = st.radio("Model:", model_options)


        prompt_selection = st.radio("Prompt example:", prompt_options)
        
        prompt_example = prompt_options_dict[prompt_selection]
        
        prompt_text = st.text_area("Prompt",
            #value=,
            value=prompt_example,
            height=300,
            help="What you want to know about the image.",
            label_visibility="collapsed")
        
        go_button = st.button("Go", type="primary")
        
        
    with col3:
        st.subheader("Result")

        if go_button:
            with st.spinner("Processing..."):
                
                if uploaded_file:
                    image_bytes = uploaded_file.getvalue()
                else:
                    image_bytes = glib.get_bytes_from_file(image_options_dict[image_selection])
                
                response = glib.get_response_from_model(
                    prompt_content=prompt_text, 
                    image_bytes=image_bytes,
                    model_id=model_options_dict[model_selection]
                )
            
            st.write(response)

