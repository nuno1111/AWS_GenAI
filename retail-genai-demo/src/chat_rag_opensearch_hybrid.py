import streamlit as st
import random
from typing import Dict, Tuple, List, Union
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

from src.libs.config import load_model_config
from src.libs.opensearch import OpenSearchClient, get_opensearch_retriever
from src.libs.models import ChatModel
from src.libs.chat_utils import StreamHandler, display_chat_messages, langchain_messages_format
from src.libs.file_utils import opensearch_preprocess_document, opensearch_reset_on_click

region_name = 'us-east-1'
# st.set_page_config(page_title='친절한 매뉴얼 챗봇', page_icon="🤖", layout="wide")
# st.title("🤖 친절한 Bedrock 챗봇")

INIT_MESSAGE = {
    "role": "assistant",
    "content": "안녕하세요! 저는 Bedrock AI 챗봇입니다. 무엇을 도와드릴까요?",
}

CLAUDE_PROMPT = ChatPromptTemplate.from_messages([
    MessagesPlaceholder(variable_name="history"),
    MessagesPlaceholder(variable_name="input"),
])

def generate_response(conversation: ConversationChain, input: Union[str, List[dict]]) -> str:
    return conversation.invoke({"input": input}, {"callbacks": [StreamHandler(st.empty())]})

def render_sidebar() -> Tuple[Dict, Dict, List[st.runtime.uploaded_file_manager.UploadedFile], List]:
    with st.sidebar:
        model_config = load_model_config()
        model_name_select = st.selectbox(
            '채팅 모델 💬',
            list(model_config["models"].keys()),
            key=f"{st.session_state['widget_key']}_Model_Id",
        )
        st.session_state["model_name"] = model_name_select
        model_info = model_config["models"][model_name_select]
        model_info["region_name"] = region_name
        system_prompt_disabled = model_config.get("system_prompt_disabled", False)
        system_prompt = st.text_area(
            "시스템 프롬프트 (역할 지정) 👤",
            value="You're a nice assistant who likes to answer concisely.",
            key=f"{st.session_state['widget_key']}_System_Prompt",
            disabled=system_prompt_disabled
        )

        model_kwargs = {
            "temperature": 0.0,
            "top_p": 1.0,
            "top_k": 200,
            "max_tokens": 4096,
        }
        if not system_prompt_disabled:
            model_kwargs["system"] = system_prompt

        # uploaded_files = st.file_uploader(
        #     "파일을 선택해주세요 📎",
        #     type=["pdf"],
        #     accept_multiple_files=False,
        #     key=st.session_state["file_uploader_key"],
        # )
        uploaded_files = None
        
        # col1, col2 = st.sidebar.columns(2)

        # with col1:
        #     semantic_weight = st.slider("하이브리드 검색 강도", 0.0, 1.0, 0.51, 0.01, 
        #                                 help="1에 가까울수록 시맨틱 검색의 강도를 높입니다. 0에 가까우면 텍스트 매칭 가중치를 높입니다.", 
        #                                 key="semantic_weight_sidebar")
        #     ensemble = [semantic_weight, 1 - semantic_weight]
        #     st.session_state["ensemble"] = ensemble
        
        # with col2:
        #     st.button("지식 초기화", on_click=opensearch_reset_on_click )
    
        semantic_weight = st.slider("하이브리드 검색 강도", 0.0, 1.0, 0.1, 0.01, 
                                    help="1에 가까울수록 시맨틱 검색의 강도를 높입니다. 0에 가까우면 텍스트 매칭 가중치를 높입니다.", 
                                    key="semantic_weight_sidebar")
        ensemble = [semantic_weight, 1 - semantic_weight]
        st.session_state["ensemble"] = ensemble

    return model_info, model_kwargs, uploaded_files, ensemble


def init_session_state():
    if "widget_key" not in st.session_state:
        st.session_state["widget_key"] = str(random.randint(1, 1000000))

    if "messages" not in st.session_state:
        st.session_state["messages"] = [INIT_MESSAGE]

    if "vector_empty" not in st.session_state:
        st.session_state["vector_empty"] = True

    if "file_uploader_key" not in st.session_state:
        st.session_state["file_uploader_key"] = 0
        
from langchain.schema import Document

def extract_pdf_name_and_page(documents: List[Document]) -> List[Dict]:
    result = []
    for doc in documents:
        metadata = doc.metadata
        pdf_name = metadata.get('source', '').split('/')[-1]
        page = metadata.get('page')
        result.append({'pdf_name': pdf_name, 'page': page})
    return result

from streamlit_pdf_viewer import pdf_viewer

def chat_rag_opensearch_hybrid_main() -> None:
    prompt = st.chat_input()
    
    st.subheader("🤖 친절한 Bedrock 챗봇")
    
    init_session_state()

    model_info, model_kwargs, uploaded_files, ensemble = render_sidebar()
    
    chat_model = ChatModel(st.session_state["model_name"], model_info, model_kwargs)
    
    memory = ConversationBufferWindowMemory(k=10, ai_prefix="Assistant", chat_memory=StreamlitChatMessageHistory(), return_messages=True)
    chain = ConversationChain(
        llm=chat_model.llm,
        verbose=True,
        memory=memory,
        prompt=CLAUDE_PROMPT,
    )

    display_chat_messages(uploaded_files)
    
    

    if "os_client" not in st.session_state:
        os_client = OpenSearchClient(llm = chat_model.llm, emb = chat_model.emb)
        st.session_state["os_client"] = os_client
    else:
        os_client = st.session_state["os_client"]
        
    opensearch_preprocess_document(uploaded_files, chat_model, os_client)
    os_retriever = get_opensearch_retriever(os_client)
    
    is_vector_empty = st.session_state["vector_empty"]
    
    if prompt:
        context_text = ""
        if not is_vector_empty == True:
            context_text = os_retriever._get_relevant_documents(query = prompt, ensemble = ensemble)
        # print("context_text -> ", extract_pdf_name_and_page(context_text))
        
        prompt_new = f"Here's some context for you. However, do not mention this context unless it is directly relevant to the user's question. It is essential to deliver an answer that precisely addresses the user's needs \n<context>\n{context_text}</context>\n\n{prompt}\n\n"

        formatted_prompt = chat_model.format_prompt(prompt_new)
        st.session_state.messages.append({"role": "user", "content": formatted_prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        st.session_state["langchain_messages"] = langchain_messages_format(
            st.session_state["langchain_messages"]
        )

        if st.session_state["messages"][-1]["role"] != "assistant":
            
            
            pdf_info = "\n ###### 📒 다음은 질문과 관련된 상위 3개의 PDF페이지입니다.\n"
    
            items = extract_pdf_name_and_page(context_text)
            index = 1
            for item in items[:3]:
                pdf_info = pdf_info + "###### " + str(index) + "." + item['pdf_name'] + " / " + str(item['page']+1) + " page \n"
                index += 1
                
                    
            with st.chat_message("assistant"):
                response = generate_response(
                    chain, [{"role": "user", "content": formatted_prompt}]
                ) 
                st.write(pdf_info)
                response['response'] = response['response'] + pdf_info
                
            message = {"role": "assistant", "content": response }
            st.session_state.messages.append(message)
            
            
            # st.markdown("#### 📒 다음은 질문과 관련된 상위 3개의 PDF페이지입니다.")
            # items = extract_pdf_name_and_page(context_text)
            # for item in items[:3]:
            #     pdf_file_path = 'data/pdf/'+item['pdf_name']
            #     pdf_page = item['page']
            #     pdf_viewer(
            #         input=pdf_file_path,
            #         pages_to_render=[pdf_page+1],
            #         width=1200          
            #     )
            
            
