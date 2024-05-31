import streamlit as st
import src.image_background_lib as glib
from PIL import Image

def image_background_app_main():
    st.title("상품이미지 배경 변경")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("상품이미지")
        # uploaded_file = st.file_uploader("Select an image", type=['png', 'jpg'])
        
        # if uploaded_file:
        #     uploaded_image_preview = glib.get_bytesio_from_bytes(uploaded_file.getvalue())
        #     st.image(uploaded_image_preview)
        # else:
        #     st.image("images/필립스제품스펙.png")
        
        # # 이미지 파일 로드
        # image = Image.open("images/필립스상품메인.png")

        # (width, height) = image.size
        # # # 이미지 크기 조정
        # resized_image = image.resize((int(width/2), int(height/2)))  # 너비 500, 높이 300으로 조정

        # # # 이미지 표시
        # st.image(resized_image)
        
        st.image("images/example.jpg")

    with col2:
        st.subheader("이미지 정보")
        
        mask_prompt = st.text_input("유지할 개체:", value="car", help="The mask text")
        
        prompt_text = st.text_area("유지할 개체와 추가 배경 설명:", value="car on the highway", height=100, help="The prompt text")
        
        negative_prompt = st.text_input("배경에 있어서는 안 되는 항목:", help="The negative prompt")

        outpainting_mode = st.radio("Outpainting 모드:", ["PRECISE", "DEFAULT"], horizontal=True)
        
        generate_button = st.button("Generate", type="primary")


    with col3:
        st.subheader("결과")

        if generate_button:
            # if uploaded_file:
            #     image_bytes = uploaded_file.getvalue()
            # else:
            #     image_bytes = glib.get_bytes_from_file("images/필립스제품스펙.png")
            
            # image = Image.open("images/필립스상품메인.png")

            # (width, height) = image.size
            # # # 이미지 크기 조정
            # resized_image = image.resize((int(width/2), int(height/2)))  # 너비 500, 높이 300으로 조정
            
            # image_bytes = glib.get_file_bytes(resized_image)
            image_bytes = glib.get_bytes_from_file("images/example.jpg")
            
            with st.spinner("Drawing..."):
                generated_image = glib.get_image_from_model(
                    prompt_content=prompt_text, 
                    image_bytes=image_bytes,
                    mask_prompt=mask_prompt,
                    negative_prompt=negative_prompt,
                    outpainting_mode=outpainting_mode,
                )
            
            st.image(generated_image)
