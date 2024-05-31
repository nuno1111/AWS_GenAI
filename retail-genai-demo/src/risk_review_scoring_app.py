import streamlit as st
import src.risk_review_scoring_lib as glib

prompt_example = """다음은 홈쇼핑 리뷰 데이터입니다.
- 리뷰 : </review>
- 해당 리뷰에 대한 위험 score를 뽑으려고 합니다.
- 다음 목록과 같은 위험이 있을 경우 높은 score를 부여해주세요.
   1. 상품 하자, 변질, 이물질, 위생 문제 등으로 인해 고객이 정상적인 상품 사용이나 섭취가 어렵다고 언급한 경우
   2. 부작용, 상해 등 고객의 안전에 해가 된 경우
   3. 고객이 상담센터에 직접 연락하여 클레임한 경우
- 리뷰 결과는 다음과 같이 100점척도로 위험점수와 그렇게 점수를 매긴 이유를 xml 형태로 알려주세요.
<result>
    <score>[0-100]</score>
    <reason>[reason text]</reason>
</result>"""



def risk_review_scoring_app_main():

    st.title("위험 리뷰 분석")

    col1, col2, col3 = st.columns(3)

    model_options_dict = {
        "claude 3 - haiku": "anthropic.claude-3-haiku-20240307-v1:0",
        "claude 3 - sonnet": "anthropic.claude-3-sonnet-20240229-v1:0",
    }

    model_options = list(model_options_dict)
    
    review_options_dict = {
        "생활카테고리1": "너무 얇아요 막 사용하기에는 괜찮아요",
        "생활카테고리2": "압력전혀안되는 불량인지 설명과는다른상품 사용한 거라반품못하고 완전 실망 압력안됨 김이다 ㅁ배어나옴",
        "식품카테고리1": "생각보다 맛이 약합니다",
        "식품카테고리2": "약간 냄새가 역하고 맛있는팥맛이 아니라 화학성분이",
        "직접입력": "",
    }
    review_list = list(review_options_dict)

    with col1:
        st.subheader("Review")
            
        selected_review = st.radio(
            "review:",
            review_list,
            #label_visibility="collapsed"
        )
        
        context_for_lab = review_options_dict[selected_review]
        context_text = st.text_area("review:", value=context_for_lab, height=350)

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
                prompt_input = prompt_text.replace("</review>","<review>"+context_text+"</review>")
                response = glib.get_response_from_model(
                    prompt_content=prompt_input, 
                    model_id=model_options_dict[model_selection]
                )
            
            st.text_area("Prompt",
                value=response,
                height=600,
                label_visibility="collapsed")
    
