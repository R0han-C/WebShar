from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from supabase import create_client, Client
import os
from fastapi import FastAPI, HTTPException, Path, Query
from typing import Optional

app = FastAPI(
    title="Product and Stock Management API's",
    description=""""
    This API provides endpoints for managing products and stock in an e-commerce application. 🛒 \n
    1. There are few api's below that can do stock and transaction management 💰\n
    2. Product needs to be added first ➕ \n
    3. Transactions and counts are getting updated 📊 💰 \n
    4. Search feature is also added 🔍 \n

    """,
    version="1.0",
)

SUPABASE_URL = ""
SUPABASE_KEY = ""

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


class Product(BaseModel):
    product_name: str
    product_price: float
    product_stock_count: int


@app.get("/search_product/")
def search_product(substring: str = Query(..., title="Substring to search")):
    try:
        response = (supabase.table("products").select("*").text_search(
            "product_name", f"'{substring}'|'Mean'").execute())
        products_data = response.data

        if not products_data:
            raise HTTPException(status_code=404, detail="No products found")

        return {"products": products_data}

    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/product/{product_id}")
def get_product(product_id: int):
    try:

        response = supabase.table("products").select("*").eq(
            "id", product_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Product not found")
        return {"data": response.data}

    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/inventory")
def get_inventory():
    try:

        response = supabase.table("products").select("*").execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="No products found")
        return {"data": response.data}

    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/add/product")
def add_product(
        product_name: str = Query(...),
        product_price: float = Query(...),
        product_stock_count: int = Query(...),
):

    data = {
        "product_name": product_name,
        "product_price": product_price,
        "product_stock_count": product_stock_count,
    }
    try:
        response = supabase.table("products").insert(data).execute()
        if response:
            return {
                "message": "Product added successfully",
                "data": response.data
            }
        else:
            raise HTTPException(status_code=response.status_code,
                                detail=response.data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/update/product")
def update_product(
        product_id: int = Query(...),
        product_name: Optional[str] = Query(None),
        product_price: Optional[float] = Query(None),
        product_stock_count: Optional[int] = Query(None),
):

    try:
        existing_product_response = (supabase.table("products").select("*").eq(
            "id", product_id).execute())
        if not existing_product_response:
            raise HTTPException(status_code=404, detail="Product not found")

        update_data = {}
        if product_name is not None:
            update_data["product_name"] = product_name
        if product_price is not None:
            update_data["product_price"] = product_price
        if product_stock_count is not None:
            update_data["product_stock_count"] = product_stock_count

        if not update_data:
            raise HTTPException(status_code=400,
                                detail="No valid fields to update")

        response, count = (supabase.table("products").update(update_data).eq(
            "id", product_id).execute())
        if response:
            return {
                "message": "Product updated successfully",
                "data": response
            }
        else:
            raise HTTPException(status_code=500,
                                detail="Failed to update product")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/delete/product")
def delete_product(product_id: int = Query(...)):
    try:

        response = supabase.table("products").select("*").eq(
            "id", product_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Product not found")

        response = supabase.table("products").delete().eq(
            "id", product_id).execute()
        if response:
            return {
                "message":
                f"Product with id {product_id} deleted successfully",
                "data": response,
            }
        else:
            raise HTTPException(status_code=500,
                                detail="Failed to delete product")
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/purchase/{product_id}")
def purchase_product(
        product_id: int = Path(..., title="The ID of the product to purchase"),
        quantity: int = Query(..., gt=0, title="The quantity to purchase"),
):
    try:

        response = supabase.table("products").select("*").eq(
            "id", product_id).execute()
        product_data = response.data

        if not product_data:
            raise HTTPException(status_code=404, detail="Product not found")

        current_stock = product_data[0]["product_stock_count"]
        if current_stock < quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock")

        total_amount = product_data[0]["product_price"] * quantity

        new_stock_count = current_stock - quantity
        update_response, count = (supabase.table("products").update({
            "product_stock_count":
            new_stock_count
        }).eq("id", product_id).execute())

        if not update_response:
            raise HTTPException(status_code=500,
                                detail="Failed to update stock count")

        transaction_data = {
            "product_id": product_id,
            "transaction_type": "purchase",
            "transaction_amount": total_amount,
        }

        transaction_response = (
            supabase.table("sales").insert(transaction_data).execute())

        if not transaction_response:
            raise HTTPException(status_code=500,
                                detail="Failed to log transaction")

        return {
            "message":
            f"Successfully purchased {quantity} units of Product {product_id}",
            "total_amount": total_amount,
        }
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sales/{transaction_id}")
def see_product_transaction_by_id(transaction_id: int):
    try:

        response = (supabase.table("sales").select("*").eq(
            "id", transaction_id).execute())
        transaction_data = response.data
        if not transaction_data:
            raise HTTPException(status_code=404,
                                detail="Transaction not found")

        return {
            "transaction_id": transaction_data[0]["id"],
            "product_id": transaction_data[0]["product_id"],
            "transaction_type": transaction_data[0]["transaction_type"],
            "transaction_amount": transaction_data[0]["transaction_amount"],
            "transaction_date": transaction_data[0]["transaction_date"],
        }
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sales/product/{product_id}")
def see_all_transactions_for_product(product_id: int):
    try:

        response = (supabase.table("sales").select("*").eq(
            "product_id", product_id).execute())
        transactions_data = response.data

        total_sales_amount = sum(transaction["transaction_amount"]
                                 for transaction in transactions_data)
        total_transactions_count = len(transactions_data)

        return {
            "product_id": product_id,
            "total_transactions_count": total_transactions_count,
            "total_sales_amount": total_sales_amount,
            "transactions": transactions_data,
        }
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get_all_transactions")
def see_all_transactions():
    try:

        response = supabase.table("sales").select("*").execute()
        transactions_data = response.data

        return {
            "total_transactions_count": len(transactions_data),
            "transactions": transactions_data,
        }
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
