from atlassian import Confluence

confluence = Confluence(
    url="https://lge-web-project.atlassian.net/wiki/",
    username="nuno1026@gmail.com",
    password="ATATT3xFfGF0KS5JpjHLBVnbP8kL9r_-8hmIzoxlxCC21Q0-navImrH6Z8bagRVLNtAbExImW_kTN6whpiEZt_8lZQ7puuiPEZQyZqzVQA-flq8pCf1S7uj7WlHlX924a_oLuThJjlzUP4X7nrGyLX91SgqSpk60QK8BxWmKYffryUSZLD5hKIA=08CA530A",
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



