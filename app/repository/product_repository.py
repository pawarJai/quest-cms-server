from unittest import skip
from app.config.database import db
from bson.objectid import ObjectId




class ProductRepository:
    def _serialize_product(product: dict):
        product["id"] = str(product["_id"])
        del product["_id"]
        return product
    @staticmethod
    async def create_product(product_data: dict):
        result = await db.products.insert_one(product_data)
        return str(result.inserted_id)

    @staticmethod
    async def get_all_products():
        products = await db.products.find().to_list(500)
        for p in products:
            p["id"] = str(p["_id"])
            del p["_id"]
        return products

    @staticmethod
    async def get_product_by_id(product_id: str):
        product = await db.products.find_one({"_id": ObjectId(product_id)})
        if product:
            product["id"] = str(product["_id"])
            del product["_id"]
        return product

    @staticmethod
    async def update_product(product_id: str, update_data: dict):
        await db.products.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": update_data}
        )
        return True

    @staticmethod
    async def delete_product(product_id: str):
        await db.products.delete_one({"_id": ObjectId(product_id)})
        return True
    
    @staticmethod
    async def get_products_paginated(skip: int, limit: int):
        products = await db.products.find().skip(skip).limit(limit).to_list(limit)
        return [ProductRepository._serialize_product(p) for p in products]

    @staticmethod
    async def count_products():
        return await db.products.count_documents({})

    @staticmethod
    async def filter_products(query: dict, skip: int, limit: int):
        products = await db.products.find(query).skip(skip).limit(limit).to_list(limit)
        return [ProductRepository._serialize_product(p) for p in products]
    
    @staticmethod
    async def count_filtered_products(query: dict):
        return await db.products.count_documents(query)

