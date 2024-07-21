from flask import Flask, g, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{os.getenv('DATABASE_USER')}:{os.getenv('DATABASE_PASSWORD')}@"
    f"{os.getenv('DATABASE_HOST')}/{os.getenv('DATABASE_NAME')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define your models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)
    blog_posts = db.relationship('BlogPost', backref='author', lazy=True)

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# Initialize the database
@app.before_request
def before_request():
    if not hasattr(g, 'db_initialized'):
        db.create_all()
        g.db_initialized = True

# Utility function to check if user is logged in
def is_logged_in():
    return 'logged_in' in session

# Routes

@app.route('/')
def index():
    # Logic to fetch and display blog posts
    blog_posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template('index.html', blog_posts=blog_posts)

@app.route('/post/<int:post_id>')
def post(post_id):
    # Logic to fetch and display a single blog post
    post = BlogPost.query.get(post_id)
    return render_template('post.html', post=post)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['logged_in'] = True
            session['username'] = username
            flash('You are now logged in', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')

@app.route('/admin/new_post', methods=['GET', 'POST'])
def new_post():
    if not is_logged_in():
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        author = session['username']

        author_user = User.query.filter_by(username=author).first()
        new_post = BlogPost(title=title, content=content, author=author_user)
        db.session.add(new_post)
        db.session.commit()

        flash('Blog post created', 'success')
        return redirect(url_for('index'))

    return render_template('new_post.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        referral_code = request.form['referral_code']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        if referral_code != '4555':
            flash('Invalid referral code', 'danger')
            return redirect(url_for('signup'))

        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists', 'danger')
            return redirect(url_for('signup'))

        new_user = User(username=username, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Signup successful', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/post/<int:post_id>')
def view_post(post_id):
    post = BlogPost.query.join(User).filter(BlogPost.id == post_id).first()
    if post:
        return render_template('view_post.html', post=post)
    else:
        flash('Post not found', 'danger')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
