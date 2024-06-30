
# pip install
pip install atlassian-python-api lxml Pillow pytesseract markdownify python-dotenv requests-aws4auth

# .env파일 정보
UPSTAGE_API_KEY=[UPSTAGE_API_KEY]
CONFLUENCE_URL=[CONFLUENCE_URL]
CONFLUENCE_USERNAME=[CONFLUENCE_USERNAME]
CONFLUENCE_API_KEY=[CONFLUENCE_API_KEY]

# AOSS (Amazon Opensearch Serverless) 셋팅 참조 URL

- URL : https://github.com/sungeuns/gen-ai-sagemaker/blob/main/RAG-bedrock/02-aoss-creation.ipynb

# (아래참조) opensearch 로컬 컨테이너 세팅 - 형태소 분석기인 nori analyzer가 기본으로 설치되어 있지 않음

## opensearch image pull
docker pull public.ecr.aws/opensearchproject/opensearch:latest

## Opensearch 실행

docker run -it -p 9200:9200 -p 9600:9600 -e "OPENSEARCH_INITIAL_ADMIN_PASSWORD=Admin123!!" -e "discovery.type=single-node" -e "plugins.security.
disabled=true" -d --name opensearch-node public.ecr.aws/opensearchproject/opensearch:latest 
