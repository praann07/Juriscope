import os
import gc
import torch
import numpy as np
import logging
from transformers import AutoTokenizer, AutoModel
from langchain_core.embeddings import Embeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from src.config import config

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_global_model = None
_global_tokenizer = None


def get_global_model_and_tokenizer():
    global _global_model, _global_tokenizer
    if _global_tokenizer is None:
        logger.info("Loading tokenizer...")
        _global_tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-mpnet-base-v2")
    if _global_model is None:
        logger.info("Loading embedding model...")
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        _global_model = AutoModel.from_pretrained("sentence-transformers/all-mpnet-base-v2")
        _global_model.to(device)
        _global_model.eval()
    return _global_model, _global_tokenizer


class GlobalModelHuggingFaceEmbeddings(Embeddings):
    def __init__(self, batch_size=8):
        self.batch_size = batch_size
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model, self.tokenizer = get_global_model_and_tokenizer()

    def _mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[0]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    def embed_documents(self, texts):
        all_embeddings = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            with torch.no_grad():
                inputs = self.tokenizer(batch, padding=True, truncation=True, max_length=512, return_tensors="pt").to(self.device)
                outputs = self.model(**inputs)
                embeddings = self._mean_pooling(outputs, inputs["attention_mask"])
                embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
                all_embeddings.append(embeddings.cpu().numpy())
            del inputs, outputs, embeddings
            gc.collect()
        return np.vstack(all_embeddings).tolist()

    def embed_query(self, text):
        return self.embed_documents([text])[0]


class VectorStore:
    def __init__(self):
        self.embeddings = GlobalModelHuggingFaceEmbeddings()
        self.pc = Pinecone(api_key=config.PINECONE_API_KEY)
        self.index_name = config.INDEX_NAME
        self._ensure_index()

    def _ensure_index(self):
        existing = [i.name for i in self.pc.list_indexes().indexes]
        if self.index_name not in existing:
            logger.info(f"Creating index: {self.index_name}")
            self.pc.create_index(
                name=self.index_name,
                dimension=768,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
        else:
            logger.info(f"Index '{self.index_name}' already exists")

    def load_index(self):
        logger.info(f"Loading vectorstore: {self.index_name}")
        return PineconeVectorStore(
            index=self.pc.Index(self.index_name),
            embedding=self.embeddings,
            text_key="text"
        )
