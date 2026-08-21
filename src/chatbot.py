import logging
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from src.config import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger(__name__)


def _format_docs(docs):
    seen = set()
    unique = []
    for doc in docs:
        key = doc.page_content[:200]
        if key not in seen:
            seen.add(key)
            unique.append(doc)
    return "\n\n---\n\n".join(
        f"[Source: {doc.metadata.get('source', 'unknown')}]\n{doc.page_content}"
        for doc in unique
    )


class LegalDocumentAssistant:

    def __init__(self, vectorstore):
        self.llm = ChatGroq(
            api_key=config.GROQ_API_KEY,
            model=config.GROQ_MODEL,
            temperature=0.1,
            max_tokens=2048
        )
        self.retriever = vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 6, "fetch_k": 20, "lambda_mult": 0.7}
        )
        self.chat_history = []

    def _multi_query_retrieve(self, query: str):
        """Generate multiple query variants and merge results for better recall."""
        if not self.chat_history:
            standalone = query
        else:
            condense_prompt = ChatPromptTemplate.from_messages([
                ("system", "Rephrase the follow-up question as a standalone question preserving all legal context. Return ONLY the rephrased question, nothing else."),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}")
            ])
            standalone = (condense_prompt | self.llm | StrOutputParser()).invoke({
                "input": query,
                "chat_history": self.chat_history[-6:]
            })

        # Generate 2 additional query variants to improve retrieval coverage
        variant_prompt = ChatPromptTemplate.from_template(
            """You are a legal research assistant. Generate 2 alternative search queries for the following question to improve document retrieval.
Focus on: (1) factual/party-name angle, (2) legal-ruling angle.
Return ONLY the 2 queries, one per line, no numbering or explanation.

Question: {question}"""
        )
        variants_raw = (variant_prompt | self.llm | StrOutputParser()).invoke({"question": standalone})
        variants = [v.strip() for v in variants_raw.strip().split("\n") if v.strip()][:2]

        all_queries = [standalone] + variants
        logger.info(f"Multi-query retrieval with {len(all_queries)} queries: {all_queries}")

        all_docs = []
        for q in all_queries:
            try:
                docs = self.retriever.invoke(q)
                all_docs.extend(docs)
            except Exception as e:
                logger.warning(f"Retrieval failed for query '{q}': {e}")

        return all_docs, standalone

    def chat(self, query: str) -> str:
        if query.lower() in ["exit", "quit", "bye"]:
            return "Thank you for using Juriscope. Goodbye!"
        if not query.strip():
            return "Please enter a question about the legal documents."

        try:
            docs, standalone = self._multi_query_retrieve(query)

            if not docs:
                return "I could not find any relevant information in the indexed documents for your question."

            context = _format_docs(docs)

            history_text = ""
            for msg in self.chat_history[-6:]:
                role = "User" if isinstance(msg, HumanMessage) else "Assistant"
                history_text += f"{role}: {msg.content}\n"

            qa_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a precise and authoritative legal document assistant. Your answers must be grounded strictly in the provided context.

STRICT RULES:
1. ALWAYS use actual party names from the documents (e.g. "Rajnesh", "Neha"). NEVER substitute with "husband", "wife", "Applicant", "Respondent" if real names exist in the context.
2. Each document chunk begins with a [CASE HEADER] — extract party names, case number, and court from there.
3. For maintenance/financial questions: scan ALL chunks carefully for rupee amounts, dates, and court orders. Report every figure you find.
4. If multiple unrelated cases appear in context, answer ONLY from the case most relevant to the question. Clearly state which case you are answering from.
5. Cite paragraph numbers or section references when available.
6. If information is genuinely not in the context, say: "This information is not available in the indexed documents."
7. NEVER invent, assume, or extrapolate facts not present in the context.
8. Structure your answer clearly — use bullet points for lists of facts or amounts.

Previous conversation:
{history}

Context from indexed legal documents:
{context}"""),
                ("human", "{question}")
            ])

            answer = (qa_prompt | self.llm | StrOutputParser()).invoke({
                "question": query,
                "context": context,
                "history": history_text
            })

            self.chat_history.append(HumanMessage(content=query))
            self.chat_history.append(AIMessage(content=answer))
            if len(self.chat_history) > 20:
                self.chat_history = self.chat_history[-20:]

            return answer

        except Exception as e:
            logger.error(f"Chat error: {e}", exc_info=True)
            return "An error occurred while processing your question. Please try again."

    def reset_conversation(self):
        self.chat_history = []
        return "Conversation reset. How can I help you with the legal documents?"
