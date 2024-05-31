import streamlit as st
import src.risk_review_lib as glib

prompt_example = """다음은 홈쇼핑 리뷰 데이터를 저장하고 있는 CSV입니다. header 값도 포함되어 있습니다.
</csv>
- 다음과 같은 이슈가 있는 리뷰를 모두 선별해주세요.
   1. 상품 하자, 변질, 이물질, 위생 문제 등으로 인해 고객이 정상적인 상품 사용이나 섭취가 어렵다고 언급한 경우
   2. 부작용, 상해 등 고객의 안전에 해가 된 경우
   3. 고객이 상담센터에 직접 연락하여 클레임한 경우
- 리뷰의 요약 내용도 포함해 주세요.
- 답안은 다음 예시와 같이 '리뷰 요약' / '리뷰' / '상품명' / '상품코드'를 json 형태로 만들어주세요.
<result_example>
    [
        {
            '리뷰요약':'피스타치오에서 상한 맛이 나고 불쾌한 맛이 났음.',
            '리뷰':'가격대비 별로에요 신선하다고해 주문했는데 피스타치오에서 상한맛이나요 별 로에요 한봉지만 그런건 아니것 같아요 매일 먹는데 계속 불쾌한 맛이나요'
            '상품명':'오트리 고메넛츠2 총100봉',
            '상품코드':'37939759'
        },
        {
            '리뷰요약':'피스타치오에서 상한 맛이 나고 불쾌한 맛이 났음.',
            '리뷰':'가격대비 별로에요 신선하다고해 주문했는데 피스타치오에서 상한맛이나요 별 로에요 한봉지만 그런건 아니것 같아요 매일 먹는데 계속 불쾌한 맛이나요'
            '상품명':'오트리 고메넛츠2 총100봉',
            '상품코드':'37939759'
        },
    ]
</result_example>"""

def risk_review_app_main():

    st.title("위험 리뷰 분석")

    col1, col2, col3 = st.columns(3)

    model_options_dict = {
        "claude 3 - haiku": "anthropic.claude-3-haiku-20240307-v1:0",
        "claude 3 - sonnet": "anthropic.claude-3-sonnet-20240229-v1:0",
    }

    model_options = list(model_options_dict)
    
    with col1:
        st.subheader("Context")
    
        context_list = glib.get_context_list()
        
        selected_context = st.radio(
            "Lab context:",
            context_list,
            #label_visibility="collapsed"
        )
        
        with st.expander("See context"):
            context_for_lab = glib.get_context(selected_context)
            context_text = st.text_area("Context text:", value=context_for_lab, height=350)
        
    with col2:
        st.subheader("Prompt")
        
        model_selection = st.radio("Model select", model_options)
        
        # model_example = model_options_dict[model_selection]
        
        prompt_text = st.text_area("Prompt",
            value=prompt_example,
            height=400,
            help="Promt를 입력해주세요.",
            label_visibility="collapsed")
        
        go_button = st.button("Go", type="primary")
        
        
    with col3:
        st.subheader("Result")
        # print(model_options_dict[model_selection])
        if go_button:
            with st.spinner("Processing..."):
                prompt_input = prompt_text.replace("</csv>","<csv>"+context_text+"</csv>")
                response = glib.get_response_from_model(
                    prompt_content=prompt_input, 
                    model_id=model_options_dict[model_selection]
                )
            
            st.text_area("Prompt",
                value=response,
                height=600,
                label_visibility="collapsed")
    
