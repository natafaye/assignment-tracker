from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
assignment = Table('assignment', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('title', String(length=64)),
    Column('description', String(length=500)),
    Column('due_date', DateTime),
    Column('course_id', Integer),
)

submission = Table('submission', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('time', DateTime),
    Column('user_id', Integer),
    Column('assignment_id', Integer),
    Column('content', String(length=2500)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['assignment'].columns['course_id'].create()
    post_meta.tables['submission'].columns['assignment_id'].create()
    post_meta.tables['submission'].columns['user_id'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['assignment'].columns['course_id'].drop()
    post_meta.tables['submission'].columns['assignment_id'].drop()
    post_meta.tables['submission'].columns['user_id'].drop()
