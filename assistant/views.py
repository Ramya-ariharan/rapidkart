# from django.shortcuts import render

# # Create your views here.
# from rest_framework.views import APIView

# from rest_framework.response import Response

# from openai import OpenAI

# from django.conf import settings

# from .vector_store import (
#     search_products
# )


# client = OpenAI(
#     api_key=settings.OPENAI_API_KEY
# )


# class ShoppingAssistantView(APIView):
#  def post(self, request):

#         query = request.data.get(
#             'query'
#         )

#         matched_products = search_products(
#             query
#         )

#         product_context = "\n".join([

#             f"{p.name} - {p.description} - ₹{p.price}"

#             for p in matched_products
#         ])

#         prompt = f"""

#         You are an intelligent shopping assistant.

#         User Query:
#         {query}

#         Available Products:
#         {product_context}

#         Recommend products naturally.

#         Mention benefits.

#         Keep response concise.
#         """

#         ai_response = client.chat.completions.create(

#             model='gpt-4.1-mini',

#             messages=[
#                 {
#                     'role': 'user',
#                     'content': prompt
#                 }
#             ]
#         )

#         products_data = []

#         for product in matched_products:

#             image = product.images.first()

#             products_data.append({

#                 'id': product.id,

#                 'name': product.name,

#                 'description': product.description,

#                 'price': product.price,

#                 'stock': product.stock,

#                 'image': (
#                     image.image.url
#                     if image else None
#                 )
#             })

#         return Response({

#             'query': query,

#             'assistant_message': (
#                 ai_response
#                 .choices[0]
#                 .message
#                 .content
#             ),

#             'products': products_data
#         })



import re
import numpy as np

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.conf import settings
from django.db.models import Q

from openai import OpenAI

from products.models import Product
from products.serializers import ProductSerializer

from sentence_transformers import SentenceTransformer
import faiss


# -----------------------------------------
# LOAD EMBEDDING MODEL
# -----------------------------------------

embedding_model = SentenceTransformer(
    'all-MiniLM-L6-v2'
)


# -----------------------------------------
# OPENAI CLIENT
# -----------------------------------------

client = OpenAI(
    api_key=settings.OPENAI_API_KEY
)


# -----------------------------------------
# BUILD PRODUCT VECTORS
# -----------------------------------------

products = Product.objects.filter(
    is_available=True
)

product_texts = [
    f"{product.name} {product.description} {product.category.name}"
    for product in products
]

product_embeddings = embedding_model.encode(
    product_texts
)

dimension = product_embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(
    np.array(product_embeddings).astype('float32')
)


# -----------------------------------------
# AI SHOPPING ASSISTANT
# -----------------------------------------


class ShoppingAssistantView(APIView):

    def post(self, request):

        query = request.data.get("query")

        if not query:
            return Response(
                {"error": "Query is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # -----------------------------------------
        # EXTRACT BUDGET
        # -----------------------------------------

        query_lower = query.lower()

        budget_patterns = [
            r'below\s+(\d+)',
            r'under\s+(\d+)',
            r'less than\s+(\d+)',
            r'within\s+(\d+)'
        ]

        max_price = None

        for pattern in budget_patterns:
            match = re.search(pattern, query_lower)
            if match:
                max_price = int(match.group(1))
                break

        # -----------------------------------------
        # CREATE QUERY EMBEDDING
        # -----------------------------------------

        query_embedding = embedding_model.encode([query])

        print("queryemb",query_embedding)

        # -----------------------------------------
        # SEARCH SIMILAR PRODUCTS
        # -----------------------------------------

        k = 20 #top 20 matches

        distances, indices = index.search(
            np.array(query_embedding).astype('float32'),
            k
        )


        print("dis and ind", distances,indices)


        product_list = list(products)

        # -----------------------------------------
        # SCORE AND RANK BY KEYWORD RELEVANCE
        # -----------------------------------------

        query_words = set(query_lower.split())

        print("queryword",query_words)

        scored_products = []

        for i, idx in enumerate(indices[0]):#np 2d array thats why 0 so first query embedding
            product = product_list[int(idx)]
            product_text = (
                product.name.lower() + " " + product.description.lower()
            )
            keyword_score = sum(
                1 for word in query_words if word in product_text
            )
            faiss_score = float(distances[0][i])

            print("faissscore491 ",faiss_score)

            scored_products.append((product.id, keyword_score, faiss_score))

        scored_products.sort(key=lambda x: (-x[1], x[2]))

        print("scrd_prod 497: ",scored_products)

        matched_product_ids = [item[0] for item in scored_products]



        matched_products = Product.objects.filter(
            id__in=matched_product_ids,
            is_available=True
        )


        print("matched_products 509",matched_products)
        # -----------------------------------------
        # APPLY PRICE FILTER
        # -----------------------------------------

        if max_price:
            matched_products = matched_products.filter(price__lte=max_price)

        # -----------------------------------------
        # OPTIONAL CATEGORY FILTERS
        # -----------------------------------------

        kitchen_keywords = [
            "kitchen", "cooking", "food", "preparing",
            "meal", "vessel", "bowl", "container", "fridge organizer"
        ]

        beauty_keywords = [
            "beauty", "skin", "skincare", "skin routine",
            "shine", "glow", "hair", "hair growth", "oil", "dull"
        ]

        sports_keywords = [
            "gym", "fitness", "sports", "workout",
            "muscle", "power", "immune",
            "swimming", "swim", "pool", "aqua",
            "cycling", "cycle", "bike",
            "running", "run", "jog",
            "yoga", "pilates", "stretch",
            "boxing", "boxing gloves", "punching",
            "cricket", "football", "basketball",
            "badminton", "tennis", "volleyball",
            "trekking", "hiking", "camping", "climbing",
            "archery", "kayak", "snorkel",
            "outdoor", "adventure", "training",
            "strength", "cardio", "endurance",
            "weight", "dumbbell", "kettlebell",
            "resistance", "band", "rope"
        ]

        books_keywords = [
            "book", "productivity", "reading", "knowledge"
        ]

        if any(word in query_lower for word in kitchen_keywords):
            matched_products = matched_products.filter(
                category__name__icontains="Home"
            )
        elif any(word in query_lower for word in beauty_keywords):
            matched_products = matched_products.filter(
                category__name__icontains="Beauty"
            )
        elif any(word in query_lower for word in sports_keywords):
            matched_products = matched_products.filter(
                category__name__icontains="Sports"
            )
        elif any(word in query_lower for word in books_keywords):
            matched_products = matched_products.filter(
                category__name__icontains="Books"
            )

        # -----------------------------------------
        # PRESERVE RANKING ORDER
        # -----------------------------------------

        matched_products_dict = {p.id: p for p in matched_products}
        ordered_products = [
            matched_products_dict[pid]
            for pid in matched_product_ids
            if pid in matched_products_dict
        ]

        # -----------------------------------------
        # LIMIT RESULTS
        # -----------------------------------------

        ordered_products = ordered_products[:5]

        # -----------------------------------------
        # CHECK IF PRODUCTS EXIST
        # -----------------------------------------

        if not ordered_products:
            return Response(
                {
                    "query": query,
                    "assistant_message": "Sorry, I couldn't find any products matching your query.",
                    "products": []
                },
                status=status.HTTP_200_OK
            )

        # -----------------------------------------
        # PREPARE PRODUCT CONTEXT
        # -----------------------------------------

        product_context = "\n".join([
            f"""
            Product Name: {product.name}
            Category: {product.category.name}
            Description: {product.description}
            Price: ₹{product.price}
            """
            for product in ordered_products
        ])

        # -----------------------------------------
        # AI RESPONSE
        # -----------------------------------------

        prompt = f"""
        You are an intelligent ecommerce shopping assistant.

        The user asked: {query}

        Here are the ONLY available products you can recommend from:
        {product_context}

        Rules:
        - Recommend ONLY the products that are directly relevant to the user's query.
        - If a product is clearly unrelated to the query, do NOT mention it at all.
        - Do NOT invent or suggest products that are not in the list above.
        - Briefly explain in one line why each recommended product suits the user's query.
        - Keep the response short and friendly.
        - If user query is not related to product its personal means answer like a marketing person of our app
        - give appropriate answer if they greet means greet too and be kind and polite reply
        """

        completion = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        assistant_message = completion.choices[0].message.content

        # -----------------------------------------
        # SERIALIZE PRODUCTS
        # -----------------------------------------

        serialized_products = ProductSerializer(
            ordered_products,
            many=True
        ).data

        # -----------------------------------------
        # FINAL RESPONSE
        # -----------------------------------------

        return Response(
            {
                "query": query,
                "assistant_message": assistant_message,
                "products": serialized_products
            },
            status=status.HTTP_200_OK
        )