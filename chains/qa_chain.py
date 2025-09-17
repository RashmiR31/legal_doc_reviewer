from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.prompts import PromptTemplate

def build_retriever(index, k=4):
    return index.as_retriever(search_type="similarity", search_kwargs={"k": k})

def build_llm(model="gpt-3.5-turbo"):
    return ChatOpenAI(model=model, temperature=0)

def build_simple_qa(llm, retriever):
    return RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True)

def build_conversational_qa(llm, retriever):
    prompt = PromptTemplate.from_template(
        "Given chat history and a follow-up question, rewrite it standalone:\n\n{chat_history}\n\nFollow-up: {question}\n\nStandalone:"
    )
    return ConversationalRetrievalChain.from_llm(llm=llm, retriever=retriever,
                                                condense_question_prompt=prompt,
                                                return_source_documents=True)
