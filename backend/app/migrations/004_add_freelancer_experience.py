"""
Migration 004: Add freelancer experience to CV sections
"""
from sqlalchemy import text


async def upgrade(connection):
    """Add freelancer experience"""

    # Insert freelancer experience
    await connection.execute(text("""
        INSERT INTO cv_sections (section_type, content, embedding, metadata)
        VALUES (
            'EXPERIENCE',
            'Freelancer (2016-2019) - Built eCommerce stores using MERN stacks for startups. I developed eCommerce websites that focus on improving user experience, which led to more profit and better customer satisfaction.',
            NULL,
            NULL
        )
        ON CONFLICT DO NOTHING
    """))

    print("✓ Migration 004: Added freelancer experience")


async def downgrade(connection):
    """Revert changes"""

    # Remove freelancer experience
    await connection.execute(text("""
        DELETE FROM cv_sections WHERE section_type = 'EXPERIENCE' AND content LIKE '%Freelancer%'
    """))

    print("✓ Migration 004: Rolled back")
