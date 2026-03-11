"""
Migration 005: Add GitHub contact and new projects
"""
from sqlalchemy import text

async def upgrade(connection):
    """Add GitHub to Contact section and new projects"""
    new_sections = [
        {
            "section_type": "CONTACT",
            "content": "GitHub: https://github.com/Thi-tran"
        },
        {
            "section_type": "PROJECTS",
            "content": "Bayesian model to predict recession: Used economic data and Hamiltonian Monte Carlo to build a statistical model predicting months until recession. Analyzed time-series economic indicators with probabilistic inference."
        },
        {
            "section_type": "PROJECTS",
            "content": "Recipe recommendation system based on goal: Built a RAG system using vector embeddings to match recipes with user fitness goals. Leverages similarity search on recipe descriptions and ingredients to recommend meals for specific objectives like weight loss and muscle gain."
        }
    ]
    
    for section in new_sections:
        await connection.execute(text("""
            INSERT INTO cv_sections (section_type, content, embedding, metadata)
            VALUES (:section_type, :content, NULL, NULL)
        """), {
            "section_type": section["section_type"],
            "content": section["content"]
        })
    
    print(f"✓ Migration 005: Inserted {len(new_sections)} new CV sections (GitHub contact + 2 projects)")


async def downgrade(connection):
    """Remove GitHub contact and new projects"""
    await connection.execute(text("""
        DELETE FROM cv_sections 
        WHERE (section_type = 'CONTACT' AND content LIKE '%github%')
        OR (section_type = 'PROJECTS' AND (
            content LIKE '%Bayesian%recession%' 
            OR content LIKE '%Recipe recommendation%'
        ))
    """))
    
    print("✓ Migration 005: Rolled back")
