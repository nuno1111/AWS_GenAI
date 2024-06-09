from opensearchpy import OpenSearch

# OpenSearch 클라이언트 생성
client = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 9200}],
    http_auth=('admin', 'Admin123!!')
)

# 인덱스 조회
indices = client.indices.get_alias("*")

# 결과 출력
for index, info in indices.items():
    print(f"Index: {index}")
    for alias, alias_info in info['aliases'].items():
        print(f"  Alias: {alias}")