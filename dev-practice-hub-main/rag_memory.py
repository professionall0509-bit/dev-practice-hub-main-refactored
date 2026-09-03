"""
Vector-store memory over tracked job applications, for semantic
Q&A like "which companies have I heard back from this month?"

Previously this module used `os.getenv(...)` without importing
`os` at all — a guaranteed NameError on the very first line executed.
It also used an in-memory chromadb.Client(), so all embeddings were
lost every time the process restarted. Both are fixed here.
"""

import os

import chromadb
from openai import OpenAI


class RAGMemory:
    def __init__(self, persist_directory="chroma_store", api_key=None):
        self.client_llm = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.chroma = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.chroma.get_or_create_collection("job_applications")

    def _embed(self, text):
        response = self.client_llm.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )
        return response.data[0].embedding

    def store_job(self, job):
        """Store a job record in the vector DB for later retrieval."""
        text = f"{job['company']} {job['role']} {job['status']} {job['subject']}"

        self.collection.upsert(
            documents=[text],
            embeddings=[self._embed(text)],
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

        q_embed = self._embed(question)
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

        response = self.client_llm.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
