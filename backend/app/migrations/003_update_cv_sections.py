"""
Migration 003: Update CV sections - final year of master and contact information
"""
from sqlalchemy import text


async def upgrade(connection):
    """Update master education entry and add contact information"""

    # Update master degree to reflect final year
    await connection.execute(text("""
        UPDATE cv_sections
        SET content = 'Final year Master of Software and Service Engineering from Aalto University. GPA: 4/5.0. Relevant coursework: Software Architecture, Cloud Computing, Service Engineering, Machine Learning.'
        WHERE section_type = 'EDUCATION'
        AND content LIKE '%Aalto University%'
    """))

    # Insert contact information if not already present
    await connection.execute(text("""
        INSERT INTO cv_sections (section_type, content, embedding, metadata)
        VALUES (
            'CONTACT',
            'Email: thi.tran.fi@gmail.com. Location: Helsinki, Finland. Phone: +358 50 470 4813.',
            NULL,
            NULL
        )
        ON CONFLICT DO NOTHING
    """))

    print("✓ Migration 003: Updated master degree year and added contact information")


async def downgrade(connection):
    """Revert changes"""

    # Revert master degree content
    await connection.execute(text("""
        UPDATE cv_sections
        SET content = 'Master of Software and Service Engineering from Aalto University (last year). GPA: 4/5.0.'
        WHERE section_type = 'EDUCATION'
        AND content LIKE '%Aalto University%'
    """))

    # Remove contact section
    await connection.execute(text("""
        DELETE FROM cv_sections WHERE section_type = 'CONTACT'
    """))

    print("✓ Migration 003: Rolled back")
