import hashlib


def create_content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def chunk_text_by_words(
        text: str,
        max_words: int = 100,
        overlap_words: int = 40
) -> list[dict]:
   words = text.split()

   if not words:
       return []
   
   chunks = []
   start = 0
   chunk_index = 0

   while start < len(words):
       end = start + max_words
       chunk_words = words[start:end]
       chunk_text = " ".join(chunk_words)

       chunks.append(
           {
               "chunk_index": chunk_index,
               "chunk_text": chunk_text,
               "token_count": len(chunk_words),
               "content_hash": create_content_hash(chunk_text)
           }
       )

       chunk_index += 1

       if end > len(words):
           break
       
       start = end - overlap_words

   return chunks
