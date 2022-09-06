import os
import subprocess

from sqlalchemy import create_engine, update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, BIGINT, SMALLINT, BOOLEAN, TIMESTAMP
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Devlog(Base):
    __tablename__ = 'devlogs'
    channel_id = Column(BIGINT)
    user_id = Column(BIGINT)
    archived = Column(BOOLEAN)
    archived_date = Column(TIMESTAMP)

    def __repr__(self):
        return f"<Devlog(self.devlog_id=, self.channel_id=, self.user_id=, self.archived=, self.archived_date="


class Author(Base):
    __tablename__ = 'authors'
    author_id = Column(BIGINT, primary_key=True)
    user_id = Column(BIGINT)
    devlogs_amount = Column(SMALLINT)

    def __repr__(self):
        return


class SQLWorker:

    def __init__(self):
        # final_db_url = None || MARKED FOR DELETION ||
        if 'DATABASE_URL' in os.environ:
            final_db_url = "postgresql+psycopg2://" + os.environ['DATABASE_URL'][11:]
        else:
            raw_db_url = subprocess.run(
                ["heroku", "config:get", "DATABASE_URL", "--app", 'pgd-bot'],
                shell=True, capture_output=True).stdout
            # Convert binary string to a regular string & remove the newline character
            db_url = raw_db_url.decode("utf-8")[11:-1]
            # Convert "postgres://<db_address>"  --> "postgresql+psycopg2://<db_address>" needed for SQLAlchemy
            final_db_url = "postgresql+psycopg2://" + db_url

        # Create SQLAlchemy engine
        self.engine = create_engine(final_db_url, connect_args={'sslmode': 'require'})
        session = sessionmaker(self.engine)
        self.session = session()

    # region Devlogs
    def add_devlog(self, channel_id, user_id):
        devlog = Devlog(channel_id=channel_id, user_id=user_id, archived=False)
        self.session.add(devlog)
        self.session.commit()
        return devlog

    def get_devlog_by_user(self, user_id):
        devlogs = self.session.query(Devlog)
        for devlog in devlogs:
            if devlog.user_id == user_id:
                return devlog

    def get_devlog_by_channel(self, channel_id):
        devlogs = self.session.query(Devlog)
        for devlog in devlogs:
            if devlog.channel_id == channel_id:
                return devlog

    def update_devlog(self, channel_id, data):
        devlog: Devlog = self.get_devlog_by_channel(channel_id)
        devlog.user_id = data['user_id']
        devlog.archived = data['archived']
        devlog.archived_date = data['archived_date']
        self.session.execute(update(Devlog).
                             where(Devlog.channel_id == devlog.channel_id).
                             values(
            user_id=devlog.user_id, archived=devlog.archived, archived_date=devlog.archived_date))
        self.session.commit()
        return devlog

    def devlog_change_owner(self, channel_id, user_id):
        devlog: Devlog = self.get_devlog_by_channel(channel_id)
        devlog.user_id = user_id
        self.session.execute(update(Devlog).
                             where(Devlog.channel_id == devlog.channel_id).
                             values(user_id=devlog.user_id))
        self.session.commit()
        return devlog

    def delete_devlog(self, devlog: Devlog):
        self.session.delete(devlog)
        self.session.commit()
    # endregion

    # region Authors
    def add_author(self, user_id):
        author: Author = Author(user_id=user_id, devlogs_amount=1)
        self.session.add(author)
        self.session.commit()

    def get_author(self, user_id):
        authors = self.session.query(Author)
        for author in authors:
            if author.user_id == user_id:
                return author

    def increase_devlog_amount(self, user_id):
        author: Author = self.get_author(user_id)
        author.devlogs_amount += 1
        self.session.execute(update(Author).
                             where(author.user_id == author.user_id).
                             values(devlogs_amount=author.devlogs_amount))
    # endregion
