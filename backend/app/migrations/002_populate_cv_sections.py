"""
Migration 003: Populate sample CV sections
"""
from sqlalchemy import text

async def upgrade(connection):
    """Insert sample CV sections"""
    cv_sections = [
        {
            "section_type": "SUMMARY",
            "content": "Full-stack developer with 5+ years of experience building web applications using Python, FastAPI, TypeScript, and React. Passionate about creating efficient, scalable solutions with clean code."
        },
        {
            "section_type": "SKILLS",
            "content": "Python, FastAPI, PostgreSQL, TypeScript, React, Next.js, Node.js, Docker, Kubernetes, AWS, Git, REST APIs, GraphQL, Vector Databases, Machine Learning"
        },
        {
            "section_type": "EXPERIENCE",
            "content": "Senior Backend Engineer at TechCorp (2021-Present): Led development of microservices architecture handling 1M+ daily requests. Built real-time analytics system using vector embeddings and PostgreSQL."
        },
        {
            "section_type": "EXPERIENCE",
            "content": "Full Stack Developer at StartupXYZ (2019-2021): Developed e-commerce platform with React frontend and FastAPI backend. Implemented search functionality using embeddings and vector similarity."
        },
        {
            "section_type": "EDUCATION",
            "content": "Bachelor of Science in Computer Science from State University (2019). GPA: 3.8/4.0. Relevant coursework: Data Structures, Algorithms, Database Design, Web Development"
        },
        {
            "section_type": "PROJECTS",
            "content": "AI-Powered CV Chat Bot: Built a semantic search system using embeddings to answer questions about CV information. Stack: FastAPI, PostgreSQL with pgvector, Next.js, Ollama LLM."
        },
        {
            "section_type": "PROJECTS",
            "content": "Real-time Analytics Dashboard: Created interactive dashboard for monitoring system metrics. Used React, WebSockets, and PostgreSQL time-series data. Handles 10k+ events/second."
        },
        {
            "section_type": "CERTIFICATIONS",
            "content": "AWS Solutions Architect Associate (2023), Kubernetes Certified Application Developer (2022), PostgreSQL Administration Specialist (2021)"
        },
    ]
    
    for section in cv_sections:
        await connection.execute(text("""
            INSERT INTO cv_sections (section_type, content, embedding, metadata)
            VALUES (:section_type, :content, NULL, NULL)
            ON CONFLICT DO NOTHING
        """), {
            "section_type": section["section_type"],
            "content": section["content"]
        })
    
    print(f"✓ Migration 003: Inserted {len(cv_sections)} CV sections")


async def downgrade(connection):
    """Remove CV sections"""
    await connection.execute(text("""
        DELETE FROM cv_sections
    """))
    
    print("✓ Migration 003: Rolled back")
