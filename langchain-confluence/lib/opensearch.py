from opensearchpy import OpenSearch
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import botocore
import time
import boto3

from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()
aoss_endpoint = os.getenv("AOSS_ENDPOINT")
aoss_collection=os.getenv("AOSS_COLLECTION")
aoss_vector_index=os.getenv("AOSS_VECTOR_INDEX")

# boto3 세션 생성
session = boto3.Session()

# 현재 세션의 리전 정보 가져오기
region = session.region_name
credentials = session.get_credentials()

## AOSS Client 정보 셋팅
client = boto3.client('opensearchserverless')
service = 'aoss'

awsauth = AWS4Auth(credentials.access_key, credentials.secret_key,
                   region, service, session_token=credentials.token)


def getOpenSearchClient():
    
    aoss_client = OpenSearch(
        hosts=[{'host': aoss_endpoint, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        timeout=6000
    )
    return aoss_client

# index 생성 함수
def createIndex(index_name, index_schema=None):    
    client = getOpenSearchClient()

    if index_schema:
        response = client.indices.create(index_name, body=index_schema)
    else:
        response = client.indices.create(index_name)
    print('\nCreating index:')
    print(response)
    
    return response

# index 생성 스키마 정보
ef_search = 512
embedding_model_dimensions = 1024

index_schema = {
        "settings": {
            "index": {
                "knn": True,
                "knn.algo_param.ef_search": ef_search,
            }
        },
        "mappings": {
            "properties": {
                "content_embeddings": {
                    "type": "knn_vector",
                    "dimension": embedding_model_dimensions,
                    "method": {
                        "name": "hnsw",
                        "space_type": "cosinesimil",
                        # "space_type": "l2",
                        "engine": "nmslib",
                        "parameters": {"ef_construction": 512, "m": 16},
                    },
                },
                "content": {"type": "text", "analyzer": "nori"},
                "metadata": {"type": "object"},
            }
        },
    }

## 인덱스 생성
# vector_index_name = "rag-hol-index-vector"
# createIndex(vector_index_name, index_schema)


## 인덱스 조회
# aoss_client = getOpenSearchClient()
# response = aoss_client.indices.get(aoss_vector_index)
# print(response)


## (참조) Local OpenSearch 클라이언트 생성
# client = OpenSearch(
#     hosts=[{'host': 'localhost', 'port': 9200}],
#     http_auth=('admin', 'Admin123!!')
# )