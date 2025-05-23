from typing import Iterator

import langchain
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import BaseMessageChunk
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.tools import tool
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
import sqlite3
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent

from util.funcs import extract_sql

# === Load Embedding Model and LLM ===
embedding_model = HuggingFaceEmbeddings(model_name="thenlper/gte-small")
llm = ChatGroq(
    model_name="llama3-70b-8192",
    temperature=0,
    groq_api_key="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",
    streaming=True
)

# === Load Vectorstore for unstructured data ===
vectorstore = FAISS.load_local("vector_store_faq_and_general_info/aou_faq_vectorstore", embedding_model,
                               allow_dangerous_deserialization=True)
# retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
retriever = vectorstore.as_retriever()
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff",
    return_source_documents=False
)
sql_system_prompt = """You are an expert SQL assistant that helps users query a university database.
For the given database, analyze the user's question, create appropriate SQL queries, and provide clear answers.
Always show your reasoning step by step.

The database has the following structure with bilingual support (English and Arabic):

1. AcademicStaff (Academic faculty and staff)
   - id (TEXT, PRIMARY KEY): Unique identifier for academic staff
   - name (TEXT): Name in English
   - nameArabic (TEXT): Name in Arabic
   - title (TEXT): Academic title in English
   - titleArabic (TEXT): Academic title in Arabic
   - email (TEXT): Contact email
   - biography (TEXT): Biography in English
   - biographyArabic (TEXT): Biography in Arabic
   - office_hours (TEXT): Office hours information
   - specialization (TEXT): Field of specialization in English
   - specializationArabic (TEXT): Field of specialization in Arabic
   - position (TEXT): Position at the university in English
   - positionArabic (TEXT): Position at the university in Arabic
   - link (TEXT): Profile link

2. Faculty (Academic departments)
   - id (TEXT, PRIMARY KEY): Unique identifier for faculty
   - name (TEXT): Faculty name in English
   - nameArabic (TEXT): Faculty name in Arabic
   - description (TEXT): Description in English
   - descriptionArabic (TEXT): Description in Arabic
   - HeadOfFaculty (TEXT, FOREIGN KEY → AcademicStaff.id): ID of faculty head
   - phoneNumber (TEXT): Contact phone number
   - email (TEXT): Contact email
   - link (TEXT): Faculty webpage link

3. Major (Study programs)
   - id (TEXT, PRIMARY KEY): Unique identifier for major
   - name (TEXT): Major name in English
   - nameArabic (TEXT): Major name in Arabic
   - requiredCredits (INTEGER): Number of credits required to complete
   - degreeLevel (TEXT): Level of degree in English
   - degreeLevelArabic (TEXT): Level of degree in Arabic
   - description (TEXT): Description in English
   - descriptionArabic (TEXT): Description in Arabic
   - studyPlan (TEXT): Study plan information
   - offeredByFaculty (TEXT, FOREIGN KEY → Faculty.id): Faculty offering this major

4. Module (Individual courses)
   - code (TEXT, PRIMARY KEY): Unique module code
   - name (TEXT): Module name in English
   - nameArabic (TEXT): Module name in Arabic
   - creditsHours (INTEGER): Credit hours for this module
   - description (TEXT): Description in English
   - descriptionArabic (TEXT): Description in Arabic
   - objectives (TEXT): Learning objectives in English
   - objectivesArabic (TEXT): Learning objectives in Arabic
   - outcomes (TEXT): Learning outcomes in English
   - outcomesArabic (TEXT): Learning outcomes in Arabic
   - prerequisite (TEXT, FOREIGN KEY → Module.code): Prerequisite module code
   - offeredByFaculty (TEXT, FOREIGN KEY → Faculty.id): Faculty offering this module

5. Teaches (Relationship between academic staff and modules)
   - staff_id (TEXT, FOREIGN KEY → AcademicStaff.id): Academic staff ID
   - module_code (TEXT, FOREIGN KEY → Module.code): Module code
   - This is a many-to-many relationship table

6. PassTutor (Teaching assistants)
   - id (TEXT, PRIMARY KEY): Unique identifier for tutor
   - name (TEXT): Tutor name in English
   - nameArabic (TEXT): Tutor name in Arabic
   - email (TEXT): Contact email
   - major (TEXT, FOREIGN KEY → Major.id): Major ID the tutor is associated with

7. PassTutorTeachingModule (Relationship between tutors and modules)
   - tutor_id (TEXT, FOREIGN KEY → PassTutor.id): Tutor ID
   - module_code (TEXT, FOREIGN KEY → Module.code): Module code
   - This is a many-to-many relationship table

8. Fee (Various fee types)
   - id (TEXT, PRIMARY KEY): Unique identifier for fee
   - feeType (TEXT): Type of fee
   - deliveryMethod (TEXT): Method of delivery
   - major_id (TEXT, FOREIGN KEY → Major.id): Associated major ID
   - feeName (TEXT): Name of the fee
   - amount (REAL): Fee amount
   - language (TEXT): Language specification

9. FAQ (Frequently asked questions)
   - id (TEXT, PRIMARY KEY): Unique identifier for FAQ
   - question (TEXT): Question in English
   - questionArabic (TEXT): Question in Arabic
   - answer (TEXT): Answer in English
   - answerArabic (TEXT): Answer in Arabic

Key relationships:
1. Academic staff teach modules through the Teaches table
2. Faculty is headed by an academic staff member (HeadOfFaculty)
3. Faculty offers multiple majors and modules
4. Modules may have prerequisites (other modules)
5. Pass tutors are associated with majors and teach modules through PassTutorTeachingModule
6. Fees are associated with majors

Common query patterns:
1. Finding modules taught by specific academic staff:
   SELECT m.* FROM Module m
   JOIN Teaches t ON m.code = t.module_code
   JOIN AcademicStaff a ON t.staff_id = a.id
   WHERE a.name LIKE '%search_term%'

2. Finding all modules in a faculty with their teachers:
   SELECT m.code, m.name, a.name as teacher_name
   FROM Module m
   JOIN Teaches t ON m.code = t.module_code
   JOIN AcademicStaff a ON t.staff_id = a.id
   WHERE m.offeredByFaculty = 'faculty_id'

3. Finding fees by major:
   SELECT m.name as major_name, f.feeName, f.amount
   FROM Fee f
   JOIN Major m ON f.major_id = m.id
   WHERE f.feeType = 'fee_type'

4. Finding tutors and the modules they teach:
   SELECT p.name as tutor_name, m.name as module_name
   FROM PassTutor p
   JOIN PassTutorTeachingModule pt ON p.id = pt.tutor_id
   JOIN Module m ON pt.module_code = m.code

When answering questions, you must:
- Handle bilingual queries by searching in both English and Arabic fields
- Use SQL queries with fuzzy logic: use LIKE, LOWER() every time to avoid case mismatch 
- Always consider synonyms, alternate phrasing, and common typos
- When any name is asked about, split the name if words> 1 and increase the search possibility by querying with LIKE for each split
- Search across all relevant columns in any table — not just one
- Avoid strict equality (=) unless you are certain the match is exact
- Prefer partial matches using LIKE or CONTAINS
- Provide thoughtful and accurate responses, even if you must search multiple fields
- When asked about tutor or any synonym close to tutor you must think of Academic Staff not Pass Tutor
- If asked about student Tutor or Pass tutor then use Pass tutor
- When asked about IT, ITC, Programming, اي تي, information technology faculty, you should use 'computer' to query. 

Be smart about schema usage and try to match intent, not just keywords.
"""

# === Load SQL Subsystem ===
db = SQLDatabase.from_uri("sqlite:///university.db")
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent_executor = create_react_agent(
    model=llm,
    tools=toolkit.get_tools(),
    state_modifier=sql_system_prompt,
    debug=True  # turn on for sql debug
)

# === Load SQL example vectorstore ===
sql_vectorstore = FAISS.load_local("vector_store_to_sql_gen/query_vector_index", embedding_model,
                                   allow_dangerous_deserialization=True)


def build_prompt_with_top_k_sql(user_question, k=5):
    retrieved = sql_vectorstore.similarity_search(user_question, k=k)
    examples = "\n\n".join([f"Q: {doc.page_content}\nSQL: {doc.metadata['sql']}" for doc in retrieved])
    return f"{examples}\n\nUser Question: {user_question}\nSQL:"


def run_sql(sql_query: str):
    try:
        with sqlite3.connect("university.db") as conn:
            cursor = conn.cursor()
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            result = "\n".join([", ".join(map(str, row)) for row in rows]) or "[No rows found.]"
            return f"{' | '.join(columns)}\n{result}"
    except Exception as e:
        return f"[SQL Error] {e}"


def hybrid_combined_summary(question: str):
    print(f"\n💬 USER QUESTION: {question}\n")

    # 1. Run vector-based retrieval
    vector_answer = qa_chain.invoke(question)

    # 2. Run SQL generation + execution
    sql_prompt = build_prompt_with_top_k_sql(question)
    sql_response = agent_executor.invoke({"messages": [("user", sql_prompt)]})["messages"][-1].content
    sql_code = extract_sql(sql_response)
    sql_output = run_sql(sql_code) if sql_code else sql_response

    # Debug outputs
    print("\n📚 VECTORSTORE RESULT:\n", vector_answer)
    print("\n🧾 SQL AGENT RAW RESPONSE:\n", sql_response)
    print("\n📊 SQL EXECUTION RESULT:\n", sql_output)

    # 3. Combine results in final summarization
    final_prompt = f"""
Here is some information from the university system.

First, retrieved from general and unstructured documents:
"{vector_answer}"

Second, retrieved from structured tabular data:
"{sql_output}"

Please write a helpful, final answer for the user based on all this information. Do not mention any source, SQL, database, tools, or technical terms.
"""
    response = llm.stream(final_prompt)
    return response


@tool
def university_info_retriever(question: str) -> str:
    """Used when asked about information Only.
    Retrieves university info using both vector store and SQL
    :arg: question (user query)
    :return: the answer to user query"""
    return "".join(chunk.content for chunk in hybrid_combined_summary(question))


@tool
def general_chatting(question: str) -> str:
    """Used for general chatting"""
    chunks = []
    for chunk in llm.stream(question):
        if hasattr(chunk, "content") and chunk.content:
            chunks.append(chunk.content)
    return "".join(chunks)



memory = InMemoryChatMessageHistory(session_id="test-session")

tools = [university_info_retriever, general_chatting]
agent_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", """You are an Arab Open University (AOU) expert providing information about various aspect with the university.
Be as helpful as possible and return as much information as possible.
Do not answer any questions that do not relate to AOU, studies, tutors, modules, etc

Do not answer any questions using your pre-trained knowledge, only use the information provided in the context.
When a tool provides an answer, always use it directly as your final answer. Do not comment on it or reflect on how helpful it was.
Each user question should be treated independently. 
Do not assume the same tool should be used for follow-up questions.
Re-evaluate the best tool for every user input based on its own meaning.
"""),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=agent_prompt)

agent_executor2 = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
)

agent_with_chat_history = RunnableWithMessageHistory(
    agent_executor2,
    # This is needed because in most real world scenarios, a session id is needed
    # It isn't really used here because we are using a simple in memory ChatMessageHistory
    lambda session_id: memory,
    input_messages_key="input",
    history_messages_key="chat_history",
)
config = {
    "configurable": {"session_id": "test-session"},
    "configurable_fields": {"stream": False},
}

# === Example Usage ===
if __name__ == "__main__":
    while True:
        query = input("Q: ")
        if query == "bye":
            print("Bye 👋")
            break
        # # === Adding user message to memory ===
        # chat_history.add_user_message(query)
        # # === Invoking the messages with history ===
        # answer = hybrid_combined_summary('\n'.join(str(item) for item in chat_history.messages))
        # # === Adding AI response to memory ===
        # chat_history.add_ai_message(answer)
        answer = agent_with_chat_history.invoke({"input": query}, config=config)
        print("\n🤖 FINAL ANSWER:\n", answer)
