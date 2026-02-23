"""
Migration 003: Populate sample CV sections
"""
from sqlalchemy import text

async def upgrade(connection):
    """Insert sample CV sections"""
    cv_sections = [
        {
            "section_type": "SUMMARY",
            "content": "Full-stack developer with 5+ years of experience building web applications using React, TypeScript, Golang, FastAPI, Python, Golang and . Passionate about creating easy to use, scalable solutions with clean code."
        },
        {
            "section_type": "SKILLS",
            "content": "Python, FastAPI, PostgreSQL, TypeScript, React, Next.js, Node.js, Docker, AWS, Git, REST APIs, GraphQL, AWS, GCP, Golang, SQL, NoSQL, pgvector, Ollama LLM, Semantic Search, Vector Embeddings"
        },
        {
            "section_type": "EXPERIENCE",
            "content": "Fullstack engineer at Smartly (2021-Present): Built and took leadership in technical discovery and feature implementation at Epic level. Architected front-end for a new service. Developed full-stack projects using JavaScript stacks. Mentored junior developers in the onboarding process and provided know-how and approaches in their tasks."
        },
        {
            "section_type": "EXPERIENCE",
            "content": "Full Stack Developer at DreamBroker (2020-2021): Built and led full-stack projects in React, Ember, Java Spring, and MySQL. Initiated Shared React components Library to improve the front-end development process. Supported junior developers in the onboarding process and provided know-how and approaches in their projects. Achievement: my latest project - Subtitle Editor - was considered an innovative project of the company in 2020. The components and approaches from the project were used for future development."
        },
        {
            "section_type": "EXPERIENCE",
            "content": "Web developer as freelancer (2019-2020): Built eCommerce stores using MERN stacks for startups. I developed eCommerce websites that focus on improving user experience, which led to more profit and better customer satisfaction."
        },
        {
            "section_type": "EDUCATION",
            "content": "Bachelor of Business Information Technology from Haaga Helia (2020). GPA: 4.3/5.0. Relevant coursework: Programming (Java), Front-end development, Data Management and Database, Machine Learning"
        },
        {
            "section_type": "EDUCATION",
            "content": "Master of Software and Service Engineering from Aalto University (last year). GPA: 4/5.0."
        },
        {
            "section_type": "PROJECTS",
            "content": "AI-Powered CV Chat Bot: Built a semantic search system using embeddings to answer questions about CV information. Stack: FastAPI, PostgreSQL with pgvector, Next.js, Ollama LLM."
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
