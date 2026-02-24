"""
Migration 004: Add Luleå University experience and fun facts to CV sections
"""
from sqlalchemy import text


async def upgrade(connection):
    """Add Luleå University experience and fun facts"""

    # Insert Luleå University experience
    await connection.execute(text("""
        INSERT INTO cv_sections (section_type, content, embedding, metadata)
        VALUES (
            'EXPERIENCE',
            'University of Luleå (2019-2020): Contributed to Web Game Application for Luleå municipality to encourage people to exercise more and live sustainably. Built features including Push Notifications for mobiles and webs, Chat Application for public and private messaging with Unread Messages Counting feature.',
            NULL,
            NULL
        )
        ON CONFLICT DO NOTHING
    """))

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

    # Insert fun fact - sauna
    await connection.execute(text("""
        INSERT INTO cv_sections (section_type, content, embedding, metadata)
        VALUES (
            'FUN_FACT',
            'I enjoy sauna very much that I have a sauna session every Wednesday which I called "KeskiSauna"',
            NULL,
            NULL
        )
        ON CONFLICT DO NOTHING
    """))

    # Insert fun fact - sports and activities
    await connection.execute(text("""
        INSERT INTO cv_sections (section_type, content, embedding, metadata)
        VALUES (
            'FUN_FACT',
            'I enjoy playing basketball on the weekends and going to the swimming pool during the weekdays. And of course, enjoy sauna in the pool too!',
            NULL,
            NULL
        )
        ON CONFLICT DO NOTHING
    """))

    print("✓ Migration 004: Added Luleå University experience, freelancer experience and fun facts")


async def downgrade(connection):
    """Revert changes"""

    # Remove Luleå University experience
    await connection.execute(text("""
        DELETE FROM cv_sections WHERE section_type = 'EXPERIENCE' AND content LIKE '%Luleå%'
    """))

    # Remove freelancer experience
    await connection.execute(text("""
        DELETE FROM cv_sections WHERE section_type = 'EXPERIENCE' AND content LIKE '%Freelancer%'
    """))

    # Remove fun facts
    await connection.execute(text("""
        DELETE FROM cv_sections WHERE section_type = 'FUN_FACT'
    """))

    print("✓ Migration 004: Rolled back")
