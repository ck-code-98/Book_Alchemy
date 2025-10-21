from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey

db = SQLAlchemy()

class Author(db.Model):
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    birth_date = Column(String)
    date_of_death = Column(String)

    def __repr__(self):
        return f"Author(id = {self.id}, name = {self.name})"

class Book(db.Model):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, autoincrement=True)
    isbn = Column(String, nullable=False, unique=True)
    title = Column(String, nullable=False)
    publication_year = Column(Integer)
    author_id = Column(Integer, ForeignKey('authors.id'))

    def __repr__(self):
        return f"Book(id = {self.id}, name = {self.title})"
