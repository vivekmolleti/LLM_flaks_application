from sentence_transformers import SentenceTransformer
from bs4 import BeautifulSoup
import requests
import chromadb
from groq import Groq


client = chromadb.Client()
collection = client.create_collection("webpage_embeddings")
client = Groq()
def scrape_and_embed_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title.string if soup.title else 'No title'
        headers = [header.get_text() for header in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]
        paragraphs = [para.get_text() for para in soup.find_all('p')]
        document = f"{title}{' '.join(headers)}{' '.join(paragraphs)}"

        embedding_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        embedding = embedding_model.encode(document)
        collection.add(
                ids=url,
                documents= document,
                embeddings = embedding
        )
    else:
        print(f"Failed to retrieve content from {url}")

def get_best_match(query):
    embedding_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    embedding = embedding_model.encode([query])

    results = collection.query(
        query_embeddings=embedding,
        n_results=5
    )
    top_results = "\n".join([" ".join(document) for document in results['documents']])
    prompt = f"Given the following content from various sources, please summarize the content and provide most accurate answer to the following data:\n\n{top_results}\n\nQuery: {query}\nAnswer:"

    chat_completion = client.chat.completions.create(
        messages = [
            {
                "role": "system",
                "content": "you are a helpful assistant who should summarize the content"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        model = "llama3-8b-8192"
    )
    response_content = chat_completion.choices[0].message.content

    return response_content if response_content else "No response Generated"
