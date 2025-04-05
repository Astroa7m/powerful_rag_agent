from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain.agents.agent_toolkits.sql.base import create_sql_agent
from langchain.agents.agent_types import AgentType

# Step 1: Connect to the SQLite database
db = SQLDatabase.from_uri("sqlite:///aou_rag.db")

# Step 2: Initialize ChatGroq with custom system prompt via Chat model
llm = ChatGroq(
        model_name="llama-3.3-70b-versatile",
    temperature=0,
    groq_api_key="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",
)

prompt_message = """
You are an expert data assistant working with a university database. 
When answering questions, you must:
- Use SQL queries with fuzzy logic: use LIKE, LOWER(), and wildcards where possible.
- Always consider synonyms, alternate phrasing, and common typos (e.g. 'AI', 'A.I.', 'Artificial Intelligence', 'Machine Learning').
- Search across all relevant columns in any table — not just one.
- Avoid strict equality (=) unless you are certain the match is exact.
- Prefer partial matches using LIKE or CONTAINS.
- Provide thoughtful and accurate responses, even if you must search multiple fields.

Be smart about schema usage and try to match intent, not just keywords.

"""

# Step 3: Create a custom SQL agent
agent_executor = create_sql_agent(
    llm=llm,
    db=db,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)

# Step 4: Run a test question
response = agent_executor.run("Who are the academic staff involved in artificial intelligence or machine learning?")
print("\n🤖 Answer:\n", response)
