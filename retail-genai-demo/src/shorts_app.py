import streamlit as st
from pathlib import Path

def shorts_app_main():
    st.title('홈쇼핑 숏츠 데모')

    # 동영상 파일 경로 설정
    video_file1 = Path("data/0101 1335_생할가전_풀리오 마사지기_LB.mp4")
    video_file2 = Path("data/shortpic_v2_0101_1335.mp4")

    # 열 생성
    # col1, col2 = st.columns([2,1])

    # with col1:
        # st.header("원본 영상")
        # video_file = open(video_file1, "rb")
        # video_bytes = video_file.read()
        # st.video(video_bytes)

    # with col2:
        # st.header("숏츠 영상")
        # video_file = open(video_file2, "rb")
        # video_bytes = video_file.read()
        # st.video(video_bytes)  # 16:9 종횡비 설정
        
    st.header("원본 영상")
    video_file = open(video_file1, "rb")
    video_bytes = video_file.read()
    st.video(video_bytes)
    
    st.header("숏츠 영상")
    video_file = open(video_file2, "rb")
    video_bytes = video_file.read()
    st.video(video_bytes)  # 16:9 종횡비 설정