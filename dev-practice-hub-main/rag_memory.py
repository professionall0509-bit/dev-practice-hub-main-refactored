"""
Vector-store memory over tracked job applications, for semantic
Q&A like "which companies have I heard back from this month?"

Uses Gemini's free-tier embeddings and chat model instead of
OpenAI, so this doesn't need any paid API access.

Previously this module used `os.getenv(...)` without importing
`os` at all — a guaranteed NameError on the very first line executed.
It also used an in-memory chromadb.Client(), so all embeddings were
lost every time the process restarted. Both are fixed here too.
"""

import os

import chromadb
import google.generativeai as genai


class RAGMemory:
    def __init__(
        self,
        persist_directory="chroma_store",
        api_key=None,
        embed_model="models/text-embedding-004",
        chat_model="gemini-1.5-flash",
    ):
        genai.configure(api_key=api_key or os.getenv("GEMINI_API_KEY"))
        self.embed_model = embed_model
        self.chat_model = genai.GenerativeModel(chat_model)

        self.chroma = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.chroma.get_or_create_collection("job_applications")

    def _embed(self, text, task_type="retrieval_document"):
        result = genai.embed_content(
            model=self.embed_model,
            content=text,
            task_type=task_type,
        )
        return result["embedding"]

    def store_job(self, job):
        """Store a job record in the vector DB for later retrieval."""
        text = f"{job['company']} {job['role']} {job['status']} {job['subject']}"

        self.collection.upsert(
            documents=[text],
            embeddings=[self._embed(text, task_type="retrieval_document")],
            ids=[job["gmail_id"]],
            metadatas=[{
                "company": job.get("company", ""),
                "role": job.get("role", ""),
                "status": job.get("status", ""),
                "date": job.get("received_date", ""),
            }],
        )

    def query_jobs(self, question, n=5):
        """Answer a natural-language question about tracked applications."""
        if self.collection.count() == 0:
            return "No job applications stored yet."

        q_embed = self._embed(question, task_type="retrieval_query")
        results = self.collection.query(query_embeddings=[q_embed], n_results=n)
        documents = results.get("documents", [[]])[0]

        if not documents:
            return "No relevant applications found."

        context = "\n".join(documents)

        prompt = f"""You are a job search assistant. Answer based only on \
these job applications:

{context}

Question: {question}

Answer concisely:"""

        response = self.chat_model.generate_content(prompt)
        return response.text
