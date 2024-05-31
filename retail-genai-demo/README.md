## python 가상환경 만들기
python -m venv venv
source ./venv/bin/activate

## Library 설치
pip install streamlit boto3 langchain pypdf faiss-cpu langchain-community opensearch-py langchain_aws pdfplumber streamlit-pdf-viewer moviepy
<!-- pip3 install -r workshop/setup/requirements.txt -U -->
pip install moviepy

## streamlit 실행
streamlit run main.py --server.maxUploadSize=500
<!-- nohup streamlit run ./main.py > streamlit.log & -->
