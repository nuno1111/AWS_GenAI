## opensearch 로컬 컨테이너 세팅

# opensearch image pull
docker pull public.ecr.aws/opensearchproject/opensearch:latest

# Opensearch 실행
docker run -it -p 9200:9200 -p 9600:9600 -e "OPENSEARCH_INITIAL_ADMIN_PASSWORD=Admin123!!" -e "discovery.type=single-node" -e "plugins.security.disabled=true" -d --name opensearch-node public.ecr.aws/opensearchproject/opensearch:latest 

# pip install
pip install atlassian-python-api lxml Pillow pytesseract markdownify python-dotenv

# .env파일 정보
UPSTAGE_API_KEY=[UPSTAGE_API_KEY]
CONFLUENCE_URL=[CONFLUENCE_URL]
CONFLUENCE_USERNAME=[CONFLUENCE_USERNAME]
CONFLUENCE_API_KEY=[CONFLUENCE_API_KEY]