from sentence_transformers import SentenceTransformer

import faiss
import numpy as np

from products.models import Product

model = SentenceTransformer(
    'all-MiniLM-L6-v2'
)


products = Product.objects.all()


product_texts = [

    f"{p.name} {p.description} {p.tags}"

    for p in products
]


embeddings = model.encode(
    product_texts
)


dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(
    dimension
)

index.add(
    np.array(embeddings)
)


def search_products(query, k=5):

    query_embedding = model.encode(
        [query]
    )

    distances, indices = index.search(
        np.array(query_embedding),
        k=k
    )

    matched_products = []

    for idx in indices[0]:

        matched_products.append(
            products[idx]
        )

    return matched_products




# from sentence_transformers import SentenceTransformer
# import faiss
# import numpy as np
# from products.models import Product

# model = SentenceTransformer('all-MiniLM-L6-v2')

# products = list(Product.objects.all())  # evaluate once

# product_texts = [
#     f"{p.name} {p.description} {p.tags}"
#     for p in products
# ]

# embeddings = model.encode(product_texts)

# dimension = embeddings.shape[1]
# index = faiss.IndexFlatL2(dimension)
# index.add(np.array(embeddings, dtype=np.float32))  # explicit dtype


# def search_products(query, k=5):
#     query_embedding = model.encode([query])
#     distances, indices = index.search(
#         np.array(query_embedding, dtype=np.float32), k=k
#     )

#     return [
#         products[idx]
#         for idx in indices[0]
#         if idx != -1  # guard against sparse results
#     ]