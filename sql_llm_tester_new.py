from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_huggingface import HuggingFaceEmbeddings
from langgraph.prebuilt import create_react_agent

# Step 1: Connect to the SQLite database
db = SQLDatabase.from_uri("sqlite:///university.db")
# Step 2: Initialize ChatGroq with custom system prompt via Chat model
llm = ChatGroq(
    model_name="llama3-70b-8192",
    temperature=0,
    groq_api_key="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",
)

# Step 3: Create SQL toolkit and agent
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# Get system message from a template or use a default one
system_prompt = """You are an expert SQL assistant that helps users query a university database.
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

# Create agent using langgraph's create_react_agent
agent_executor = create_react_agent(
    model=llm,
    tools=toolkit.get_tools(),
    state_modifier=system_prompt,
    debug=True,  # Enable verbose output,
)

# Step 4: Run a test question
"""
TEST QUERIES
-List Academic Staff and the Modules They Teach
-List Faculties and Their Head of Faculty
-List Passed Tutors and the Modules They Teach
-List Full-time Learning Fees by Major
"""


def query_database(question):
    # Execute the agent with the given question
    response = agent_executor.invoke({"messages": [("user", question)]})
    # Extract the last message from the response
    return response["messages"][-1].content



import re
import sqlite3

import re


def extract_sql_block(text: str):
    """
    Extracts SQL from either:
    - a code block marked with ```sql
    - or after the first line that starts with 'SQL:'
    """
    # Try extracting from code block
    match = re.search(r"```sql(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Fallback: Look for 'SQL:' inline
    match = re.search(r"SQL\s*:\s*(SELECT .*?;)", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Try more aggressively if needed (less strict)
    match = re.search(r"(SELECT\s+.*?;)", text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else None


def run_sql(sql_query: str, db_path="university.db"):
    """Executes SQL on your database and returns tabular result as string."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        result = "\n".join([", ".join(map(str, row)) for row in rows])
        if not result:
            result = "[No rows found.]"
        return f"{' | '.join(columns)}\n{result}"
    except Exception as e:
        return f"[SQL Execution Error] {e}"
    finally:
        conn.close()

# Add a post-processing function to ensure execution if needed
def ensure_execution(question: str):
    # Step 1: Use your agent to get the SQL or reasoning
    response = query_database(question)

    # Step 2: Try to extract SQL from the response
    sql_code = extract_sql_block(response)

    if sql_code:
        print("🔍 SQL extracted:\n", sql_code)
        # Step 3: Run the actual SQL
        sql_result = run_sql(sql_code)
        print("📊 Actual SQL Result:\n", sql_result)

        # Step 4: Return final response with real DB output
        return f"{response.strip()}\n\n📊 Actual Results:\n{sql_result}"

    else:
        print("⚠️ No SQL detected, returning original response.")
        return response


def load_sql_vectorstore(path="vector_store_to_sql_gen/query_vector_index"):
    """Loads the FAISS vectorstore for query-to-sql pairs."""
    embedding = HuggingFaceEmbeddings(model_name="thenlper/gte-small")
    return FAISS.load_local(path, embedding, allow_dangerous_deserialization=True)


def build_prompt_with_top_k_sql(user_question, vectorstore=load_sql_vectorstore(), k=5):
    """
    Retrieve top-K SQL examples and combine them with the original question.
    """
    retrieved = vectorstore.similarity_search(user_question, k=k)

    examples = "\n\n".join(
        f"Q: {doc.page_content}\nSQL: {doc.metadata['sql']}" for doc in retrieved
    )

    final_prompt = (
        f"{examples}\n\n"
        f"User Question: {user_question}\nSQL:"
    )
    print("Final user prompt", final_prompt)
    return final_prompt
# Example usage
if __name__ == "__main__":
    response = ensure_execution(build_prompt_with_top_k_sql("List all the teacher of it faculty"))
    print("\n🤖 Answer:\n", response)