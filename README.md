**Product Stock Management API Quickstart Guide 🚀**

This is a product stock and transaction management api list

## Prerequisites

Before getting started, ensure you have the following installed on your system:

- Python 3.7+
- Pip (Python package manager)
## Installation

First, clone :

```bash
git clone https://github.com/R0han-C/WebShar
cd project_directory
```

## Change Secrets

Replace Superbase url and API key :

```bash
SUPABASE_URL = "https://*****.supabase.co"
SUPABASE_KEY = "eyJh*******n9gY"
```



Next, install the dependencies using pip:

```bash
pip install -r requirements.txt
```

## Running the Application

Once the installation is complete, you can start the FastAPI application by running the following command:

```bash
uvicorn main:app --reload --host 0.0.0.0
```

This command starts the development server, and `--reload` enables auto-reloading, allowing you to see the changes in real-time.

## Accessing the API

Open your web browser and navigate to `http://localhost:8000/docs`. You will see the interactive Swagger documentation for your API. From here, you can explore the available endpoints and make test requests.


