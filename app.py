import os

import psycopg
from flask import Flask, jsonify, render_template, request
from psycopg.rows import dict_row


app = Flask(__name__)


def connection():
    return psycopg.connect(
        host=os.environ.get("DB_HOST", "db"),
        dbname=os.environ.get("POSTGRES_DB", "taskboard"),
        user=os.environ.get("POSTGRES_USER", "taskboard"),
        password=os.environ["POSTGRES_PASSWORD"],
        connect_timeout=3,
        row_factory=dict_row,
    )


def ensure_schema(conn):
    with conn.cursor() as cur:
        cur.execute(
            """CREATE TABLE IF NOT EXISTS tasks (
                 id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                 title VARCHAR(160) NOT NULL,
                 completed BOOLEAN NOT NULL DEFAULT FALSE,
                 created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
               )"""
        )
    conn.commit()


@app.get("/healthz")
def health():
    try:
        with connection() as conn:
            ensure_schema(conn)
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
    except psycopg.Error:
        app.logger.exception("Database health check failed")
        return jsonify(status="unhealthy"), 503
    return jsonify(status="ok")


@app.get("/")
def index():
    with connection() as conn:
        ensure_schema(conn)
        with conn.cursor() as cur:
            cur.execute("SELECT id, title, completed FROM tasks ORDER BY id DESC LIMIT 100")
            tasks = cur.fetchall()
    return render_template("index.html", tasks=tasks)


@app.post("/tasks")
def add_task():
    title = request.form.get("title", "").strip()
    if not title or len(title) > 160:
        return jsonify(error="Task title must be 1-160 characters"), 400
    with connection() as conn:
        ensure_schema(conn)
        with conn.cursor() as cur:
            cur.execute("INSERT INTO tasks (title) VALUES (%s) RETURNING id", (title,))
            task_id = cur.fetchone()["id"]
    return jsonify(id=task_id, title=title, completed=False), 201


@app.post("/tasks/<int:task_id>/toggle")
def toggle_task(task_id):
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE tasks SET completed = NOT completed WHERE id = %s RETURNING completed",
                (task_id,),
            )
            row = cur.fetchone()
    if row is None:
        return jsonify(error="Task not found"), 404
    return jsonify(id=task_id, completed=row["completed"])
