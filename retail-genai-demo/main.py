import streamlit as st
import src.rag_chatbot_app as rag_chatbot_app
import src.shorts_app as shorts_app
import src.summary_app as summary_app
import src.image_understanding_app as image_understanding_app
import src.image_background_app as image_background_app
import src.risk_review_app as risk_review_app
import src.risk_review_scoring_app as risk_review_scoring_app
import src.image_search_app as image_search_app
import src.chat_rag_opensearch_hybrid as chat_rag_opensearch_hybrid
import src.video_attribute_app as video_attribute_app
import src.video_attribute_app_v2 as video_attribute_app_v2
import src.video_attribute_app_v3 as video_attribute_app_v3

st.set_page_config(layout="wide")
st.sidebar.title("리테일 GenAI 데모")

# 여러 탭을 만듭니다.
selected_tab = st.sidebar.radio("데모 선택", ["방송 속성 추출 v3","방송 속성 추출 v2","방송 속성 추출 v1","방송 매뉴얼 챗봇","위험 리뷰 스코어링","위험 리뷰 분석","패션 이미지 검색","챗봇 RAG 데모","홈쇼핑 숏츠 데모","상품 리뷰 요약", "상품 이미지 분석", "상품 이미지 배경"])

if selected_tab == "방송 속성 추출 v3":
    video_attribute_app_v3.video_attribute_app_main()
elif selected_tab == "방송 속성 추출 v2":
    video_attribute_app_v2.video_attribute_app_main()
elif selected_tab == "방송 속성 추출 v1":
    video_attribute_app.video_attribute_app_main()
elif selected_tab == "방송 매뉴얼 챗봇":
    chat_rag_opensearch_hybrid.chat_rag_opensearch_hybrid_main()
elif selected_tab == "위험 리뷰 스코어링":
    risk_review_scoring_app.risk_review_scoring_app_main()
elif selected_tab == "위험 리뷰 분석":
    risk_review_app.risk_review_app_main() 
elif selected_tab == "패션 이미지 검색":
    image_search_app.image_search_app_main() 
elif selected_tab == "챗봇 RAG 데모":
    rag_chatbot_app.rag_chatbot_app_main() 
elif selected_tab == "홈쇼핑 숏츠 데모":
    shorts_app.shorts_app_main()
elif selected_tab == "상품 리뷰 요약":
    summary_app.summary_app_main()
elif selected_tab == "상품 이미지 분석":
    image_understanding_app.image_understanding_app_main()
elif selected_tab == "상품 이미지 배경":
    image_background_app.image_background_app_main()
