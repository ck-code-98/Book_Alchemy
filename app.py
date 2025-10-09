from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
from data_models import db, Author, Book
from datetime import date

app = Flask(__name__)
app.secret_key = "dev"

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
db.init_app(app)

# with app.app_context():
#     db.create_all()


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        name = request.form.get("name", "").strip()
        birth_str = request.form.get("birth_date", "").strip()
        death_str = request.form.get("date_of_death", "").strip()
        birth_date = date.fromisoformat(birth_str) if birth_str else None
        date_of_death = date.fromisoformat(death_str) if death_str else None

        db.session.add(Author(
            name=name,
            birth_date=birth_date,
            date_of_death=date_of_death))

        db.session.commit()
        return render_template("add_author.html", message="Author added!")

    return render_template('add_author.html')


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    authors = Author.query.order_by(Author.name).all()

    if request.method == 'POST':
        isbn = request.form.get("isbn", "").strip()
        title = request.form.get("title", "").strip()
        publication_year_str = request.form.get("publication_year", "").strip()
        author_id = request.form.get("author_id")

        try:
            publication_year = int(publication_year_str)
        except ValueError:
            publication_year = None

        try:
            author_id = int(author_id) if author_id is not None else None
        except ValueError:
            author_id = None

        db.session.add(Book(
            isbn=isbn,
            title=title,
            publication_year=publication_year,
            author_id=author_id))

        db.session.commit()
        return render_template("add_book.html", authors=authors, message="Book added successfully!")

    return render_template('add_book.html', authors=authors)


@app.route('/')
def home():
    sort = request.args.get('sort', 'title')
    search = request.args.get('search', '').strip()
    query = (
        db.session.query(Book, Author)
        .join(Author, Book.author_id == Author.id))

    if search:
        query = query.filter(Book.title.ilike(f'%{search}%'))

    if sort == 'author':
        query = query.order_by(Author.name)
    else:
        query = query.order_by(Book.title)

    rows = query.all()
    message = None
    if not rows:
        message = f"No books found for '{search}'." if search else "No books in database."

    return render_template('home.html', rows=rows, sort=sort, message=message)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    author_id = book.author_id

    db.session.delete(book)
    db.session.commit()

    remaining = Book.query.filter_by(author_id=author_id).count()
    if remaining < 1:
        author = Author.query.get(author_id)
        if author:
            db.session.delete(author)
            db.session.commit()
            flash(f"Book deleted. Author '{author.name}' deleted as well (no remaining books in the database).")
        else:
            flash("Book deleted")
    else:
        flash("Book deleted")

    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
