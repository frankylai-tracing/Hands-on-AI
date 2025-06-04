#!/usr/bin/env python3
import os
import aiosqlite
import asyncio
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
from typing import List, Dict, Any
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
DB_PATH = os.getenv("DB_PATH", "sample.db")
MCP_PORT = int(os.getenv("MCP_PORT", "8080"))
READ_ONLY = os.getenv("READ_ONLY", "true").lower() == "true"


# Models for request/response validation
class QueryRequest(BaseModel):
    query: str


class TableRequest(BaseModel):
    table_name: str


class SampleDataRequest(BaseModel):
    table_name: str
    count: int = 5


class FeedbackRequest(BaseModel):
    user: str
    email: str
    feedback: str


# Initialize FastMCP
app = FastMCP(
    title="SQLite MCP Server",
    description="A Model Context Protocol server for SQLite databases",
    version="0.1.0",
    host="127.0.0.1",
    port=MCP_PORT,
)


# Database connection management
async def get_db():
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db


async def init_db():
    """Initialize the database with sample tables if it doesn't exist"""
    if not os.path.exists(DB_PATH):
        db = await get_db()
        try:
            # Create products table
            await db.execute(
                """
                CREATE TABLE products (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    price REAL NOT NULL,
                    category TEXT,
                    in_stock BOOLEAN DEFAULT 1
                )
            """
            )

            # Create customers table
            await db.execute(
                """
                CREATE TABLE customers (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE,
                    signup_date TEXT
                )
            """
            )

            # Create orders table
            await db.execute(
                """
                CREATE TABLE orders (
                    id INTEGER PRIMARY KEY,
                    customer_id INTEGER,
                    order_date TEXT,
                    total_amount REAL,
                    FOREIGN KEY (customer_id) REFERENCES customers (id)
                )
            """
            )

            # Create feedback table
            await db.execute(
                """
                CREATE TABLE feedback (
                    id INTEGER PRIMARY KEY,
                    user TEXT NOT NULL,
                    email TEXT NOT NULL,
                    feedback TEXT NOT NULL,
                    submission_date TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            await db.commit()
            logger.info(f"Initialized database at {DB_PATH}")
        finally:
            await db.close()
    else:
        # Check if feedback table exists and create it if it doesn't
        db = await get_db()
        try:
            cursor = await db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='feedback'"
            )
            if not await cursor.fetchone():
                await db.execute(
                    """
                    CREATE TABLE feedback (
                        id INTEGER PRIMARY KEY,
                        user TEXT NOT NULL,
                        email TEXT NOT NULL,
                        feedback TEXT NOT NULL,
                        submission_date TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )
                await db.commit()
                logger.info("Added feedback table to existing database")
        finally:
            await db.close()


# SQL query validation to prevent SQL injection and enforce read-only mode
def validate_query(query: str) -> bool:
    query = query.strip().lower()

    # Block potentially dangerous operations
    dangerous_keywords = [
        "drop",
        "delete",
        "truncate",
        "alter",
        "update",
        "pragma",
        "attach",
        "detach",
    ]
    if READ_ONLY:
        dangerous_keywords.extend(["insert", "create", "update"])

    for keyword in dangerous_keywords:
        if query.startswith(keyword) or f" {keyword} " in f" {query} ":
            return False

    return True


# MCP tools
@app.tool("execute_query", description="Execute a SQL query on the SQLite database")
async def execute_query(request: QueryRequest) -> Dict[str, Any]:
    """Execute a SQL query on the SQLite database"""
    if not validate_query(request.query):
        return {
            "error": "Invalid query. The query contains forbidden operations or keywords.",
            "read_only_mode": READ_ONLY,
        }

    db = await get_db()
    try:
        cursor = await db.execute(request.query)
        rows = await cursor.fetchall()
        columns = (
            [column[0] for column in cursor.description] if cursor.description else []
        )

        results = []
        for row in rows:
            results.append({columns[i]: row[i] for i in range(len(columns))})

        return {"columns": columns, "rows": results, "row_count": len(results)}
    except Exception as e:
        return {"error": str(e)}
    finally:
        await db.close()


@app.tool("list_tables")
async def list_tables() -> Dict[str, Any]:
    """List all tables in the SQLite database"""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        tables = [row[0] for row in await cursor.fetchall()]
        return {"tables": tables}
    except Exception as e:
        return {"error": str(e)}
    finally:
        await db.close()


@app.tool("describe_table")
async def describe_table(request: TableRequest) -> Dict[str, Any]:
    """Get the schema of a specific table"""
    db = await get_db()
    try:
        cursor = await db.execute(f"PRAGMA table_info({request.table_name})")
        columns = await cursor.fetchall()

        schema = []
        for col in columns:
            schema.append(
                {
                    "name": col[1],
                    "type": col[2],
                    "notnull": bool(col[3]),
                    "default_value": col[4],
                    "is_primary_key": bool(col[5]),
                }
            )

        return {"table_name": request.table_name, "columns": schema}
    except Exception as e:
        return {"error": str(e)}
    finally:
        await db.close()


@app.tool("count_rows")
async def count_rows(request: TableRequest) -> Dict[str, Any]:
    """Count the number of rows in a table"""
    db = await get_db()
    try:
        cursor = await db.execute(f"SELECT COUNT(*) FROM {request.table_name}")
        count = (await cursor.fetchone())[0]
        return {"table_name": request.table_name, "row_count": count}
    except Exception as e:
        return {"error": str(e)}
    finally:
        await db.close()


@app.tool("insert_sample_data")
async def insert_sample_data(request: SampleDataRequest) -> Dict[str, Any]:
    """Insert sample data into a specified table (for demo purposes)"""
    if READ_ONLY:
        return {"error": "Cannot insert data in read-only mode"}

    count = request.count if request.count else 5
    db = await get_db()

    try:
        # Get table schema to understand what to insert
        cursor = await db.execute(f"PRAGMA table_info({request.table_name})")
        columns = await cursor.fetchall()

        if not columns:
            return {"error": f"Table {request.table_name} not found"}

        # Generate insert statements based on table type
        inserted = 0

        if request.table_name.lower() == "products":
            for i in range(count):
                await db.execute(
                    "INSERT INTO products (name, description, price, category, in_stock) VALUES (?, ?, ?, ?, ?)",
                    (
                        f"Product {i+1}",
                        f"This is a description for product {i+1}",
                        round(10.99 + i * 5.25, 2),
                        ["Electronics", "Clothing", "Home", "Books", "Food"][i % 5],
                        i % 4 != 0,  # 75% of products in stock
                    ),
                )
                inserted += 1

        elif request.table_name.lower() == "customers":
            for i in range(count):
                await db.execute(
                    "INSERT INTO customers (name, email, signup_date) VALUES (?, ?, ?)",
                    (
                        f"Customer {i+1}",
                        f"customer{i+1}@example.com",
                        f"2023-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}",
                    ),
                )
                inserted += 1

        elif request.table_name.lower() == "orders":
            # First ensure we have customers
            cursor = await db.execute("SELECT COUNT(*) FROM customers")
            customer_count = (await cursor.fetchone())[0]

            if customer_count == 0:
                return {
                    "error": "Cannot insert orders without customers. Insert customers first."
                }

            for i in range(count):
                customer_id = (i % customer_count) + 1
                await db.execute(
                    "INSERT INTO orders (customer_id, order_date, total_amount) VALUES (?, ?, ?)",
                    (
                        customer_id,
                        f"2023-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}",
                        round(50.00 + i * 12.35, 2),
                    ),
                )
                inserted += 1

        elif request.table_name.lower() == "feedback":
            for i in range(count):
                await db.execute(
                    "INSERT INTO feedback (user, email, feedback) VALUES (?, ?, ?)",
                    (
                        f"User {i+1}",
                        f"user{i+1}@example.com",
                        f"This is sample feedback #{i+1}. The service is great!",
                    ),
                )
                inserted += 1

        else:
            return {
                "error": f"Sample data generation not supported for table {request.table_name}"
            }

        await db.commit()
        return {
            "table_name": request.table_name,
            "inserted_rows": inserted,
            "success": True,
        }

    except Exception as e:
        return {"error": str(e)}
    finally:
        await db.close()


@app.tool("add_feedback")
async def add_feedback(request: FeedbackRequest) -> Dict[str, Any]:
    """Add a new feedback entry to the feedback table"""
    if READ_ONLY:
        return {"error": "Cannot add feedback in read-only mode"}

    db = await get_db()
    try:
        await db.execute(
            "INSERT INTO feedback (user, email, feedback) VALUES (?, ?, ?)",
            (request.user, request.email, request.feedback),
        )
        await db.commit()

        # Get the ID of the inserted feedback
        cursor = await db.execute("SELECT last_insert_rowid()")
        feedback_id = (await cursor.fetchone())[0]

        return {
            "success": True,
            "feedback_id": feedback_id,
            "message": "Feedback successfully added",
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        await db.close()


async def main():
    # Initialize the database with sample tables
    await init_db()

    # Start the MCP server
    logger.info(f"Starting SQLite MCP Server on port {MCP_PORT}")
    logger.info(f"Database path: {DB_PATH}")
    logger.info(f"Read-only mode: {READ_ONLY}")

    # Run the app with stdio transport (no host/port needed)
    app.run(transport="stdio")


if __name__ == "__main__":
    # Initialize the database with sample tables
    init_db()

    # Start the MCP server
    logger.info(f"Starting SQLite MCP Server on port {MCP_PORT}")
    logger.info(f"Database path: {DB_PATH}")
    logger.info(f"Read-only mode: {READ_ONLY}")
    # Initialize and run the server
    app.run(transport="sse")
