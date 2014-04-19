from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
assignment = Table('assignment', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('title', VARCHAR(length=64)),
    Column('description', VARCHAR(length=500)),
    Column('due_date', DATETIME),
    Column('course_id', INTEGER),
)

user = Table('user', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('nickname', VARCHAR(length=64)),
    Column('email', VARCHAR(length=120)),
    Column('role', SMALLINT),
    Column('course_id', INTEGER),
)

submission = Table('submission', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('time', DATETIME),
    Column('user_id', INTEGER),
    Column('assignment_id', INTEGER),
    Column('content', VARCHAR(length=2500)),
)

course = Table('course', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('title', VARCHAR(length=64)),
    Column('code', VARCHAR(length=64)),
    Column('user_id', INTEGER),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['assignment'].columns['course_id'].drop()
    pre_meta.tables['user'].columns['course_id'].drop()
    pre_meta.tables['submission'].columns['assignment_id'].drop()
    pre_meta.tables['submission'].columns['user_id'].drop()
    pre_meta.tables['course'].columns['user_id'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['assignment'].columns['course_id'].create()
    pre_meta.tables['user'].columns['course_id'].create()
    pre_meta.tables['submission'].columns['assignment_id'].create()
    pre_meta.tables['submission'].columns['user_id'].create()
    pre_meta.tables['course'].columns['user_id'].create()
