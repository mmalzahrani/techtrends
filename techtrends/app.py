import sqlite3, logging

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

db_counter = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# This function connects to database with the name `database.db`
def get_db_connection_cur():
    connection = sqlite3.connect('database.db')
    return connection

# Function to get a post using its ID
def get_post(post_id):
    global db_counter
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    db_counter = db_counter + 1
    connection.close()
    db_counter = db_counter - 1
    return post

# Function to get a post title using its ID
def get_post_title(post_id):
    global db_counter
    connection = get_db_connection_cur()
    post = connection.execute('SELECT title FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    db_counter = db_counter + 1
    connection.close()
    db_counter = db_counter - 1
    return post


# Function to get total amount of posts
def get_total_posts():
    global db_counter
    connection = get_db_connection()
    db_counter = db_counter + 1
    post = connection.execute('SELECT * FROM posts').fetchall()
    post =  len(post)
    connection.close()
    db_counter = db_counter - 1
    return post


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    global db_counter
    connection = get_db_connection()
    db_counter = db_counter + 1
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    db_counter = db_counter - 1
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    title = get_post_title(post_id)
    if post is None:
      return render_template('404.html'), 404
    else:
      app.logger.info(f'Article "{title}" retrieved!')
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info(f'Page "about" retrieved!')
    return render_template('about.html')


# Define the healthz response
@app.route('/healthz')
def healthcheck():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )

    ## log line
    app.logger.info('Status request successfull')
    return response

# Define the metrics response    
@app.route('/metrics')
def metrics():
    # Define a varible, Call get_total_posts
    total_post = get_total_posts()
    response = app.response_class(
            response=json.dumps({"status":"success","code":0,"data":{"db_connection_count":db_counter,"post_count":total_post}}),
            status=200,
            mimetype='application/json'
    )

     ## log line
    app.logger.info('Metrics request successfull')
    return response



# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    global db_counter
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            db_counter = db_counter + 1
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.info(f'article is created "{title}"')
            db_counter = db_counter - 1

            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":

    ## stream logs to app.log file
    logging.basicConfig(filename='app.log',level=logging.DEBUG)

    app.run(host='0.0.0.0', port='3111')
