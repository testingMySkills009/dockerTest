from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'wpuser'  # replace with your MySQL username
app.config['MYSQL_PASSWORD'] = 'wpuser'  # replace with your MySQL password
app.config['MYSQL_DB'] = 'myapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# Utility function to check if user is logged in
def is_logged_in():
    return 'logged_in' in session

# Routes

@app.route('/')
def index():
    # Logic to fetch and display blog posts
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM blog_posts ORDER BY created_at DESC')
    blog_posts = cur.fetchall()
    cur.close()
    return render_template('index.html', blog_posts=blog_posts)

@app.route('/post/<int:post_id>')
def post(post_id):
    # Logic to fetch and display a single blog post
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM blog_posts WHERE id = %s', [post_id])
    post = cur.fetchone()
    cur.close()
    return render_template('post.html', post=post)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM users WHERE username = %s', [username])
        user = cur.fetchone()
        cur.close()
        if user and check_password_hash(user['password_hash'], password):
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

        cur = mysql.connection.cursor()
        cur.execute('SELECT id FROM users WHERE username = %s', [author])
        author_id = cur.fetchone()['id']
        cur.execute('INSERT INTO blog_posts (title, content, author_id) VALUES (%s, %s, %s)', (title, content, author_id))
        mysql.connection.commit()
        cur.close()

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

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()

        if user:
            flash('Username already exists', 'danger')
            return redirect(url_for('signup'))

        cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, hashed_password))
        mysql.connection.commit()
        cur.close()
        flash('Signup successful', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/post/<int:post_id>')
def view_post(post_id):
    cur = mysql.connection.cursor()
    cur.execute('''
        SELECT blog_posts.title, blog_posts.content, blog_posts.created_at, users.username as author 
        FROM blog_posts 
        JOIN users ON blog_posts.author_id = users.id 
        WHERE blog_posts.id = %s
    ''', (post_id,))
    post = cur.fetchone()
    cur.close()

    if post:
        return render_template('view_post.html', post=post)
    else:
        flash('Post not found', 'danger')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

