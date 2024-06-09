from lib.custom_confluence import ConfluenceLoader
# from langchain_community.document_loaders import ConfluenceLoader
# from langchain.document_loaders.confluence import ContentFormat
from langchain.text_splitter import CharacterTextSplitter
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

url = os.getenv("CONFLUENCE_URL")
username = os.getenv("CONFLUENCE_USERNAME")
api_key = os.getenv("CONFLUENCE_API_KEY")

# Confluence 접속 정보
loader = ConfluenceLoader(
    url=url,
    username=username,
    api_key=api_key,
    # space_key="SD",
    page_ids=['63897603'],  # 로드할 페이지의 ID
    include_attachments=True,
    ocr_languages="eng+kor",
    keep_markdown_format=True
    # content_format=ContentFormat.EDITOR
    # limit=500,
)
documents = loader.load()
# print(documents)

# 텍스트 분할기 생성
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

# 데이터 분할
docs = text_splitter.split_documents(documents)

# 분할된 문서 출력
for doc in docs:
    print(doc.page_content)
    # print(doc)
