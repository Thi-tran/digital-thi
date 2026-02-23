"""
Migration 004: Fix contact information - remove name field
"""
from sqlalchemy import text


async def upgrade(connection):
    """Update contact section to remove name"""

    await connection.execute(text("""
        UPDATE cv_sections
        SET content = 'Email: thi.tran.fi@gmail.com. Location: Helsinki, Finland. Phone: +358 50 470 4813.',
            embedding = NULL
        WHERE section_type = 'CONTACT'
    """))

    print("✓ Migration 004: Removed name from contact information")


async def downgrade(connection):
    pass
