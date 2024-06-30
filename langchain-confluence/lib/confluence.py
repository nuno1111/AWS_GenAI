from atlassian import Confluence

import os
from dotenv import load_dotenv
# .env 파일 로드
load_dotenv()


url = os.getenv("CONFLUENCE_URL")
username = os.getenv("CONFLUENCE_USERNAME")
password = os.getenv("CONFLUENCE_API_KEY")



confluence = Confluence(
    url=url,
    username=username,
    password=password,
    cloud=True
)

# page = confluence.get_page_by_id(63897603, expand='body.view')
print(confluence.get_all_restrictions_for_content(63897603))
# 페이지 정보 출력
# print(f"Page Title: {page['title']}")
# print(f"Page Content: {page['body']['view']['value']}")
# print(f"Page URL: {page['_links']['webui']}")

# attachment = confluence.get_attachments_from_content(
#     page_id=63897603
# )
# print(attachment)



