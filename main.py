from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from helpers import valid_input, verify_pass

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:fancypurple@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "42prpl709nrpl"

class Blog(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    body = db.Column(db.String(5000))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, author):
        self.title = title
        self.body = body
        self.author = author
    
   

class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(40))
    blogs = db.relationship('Blog', backref='author')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['login', 'index', 'signup', 'blogs']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route("/", methods=['GET'])
def index():
    
    authors = User.query.all()
    return render_template('index.html', main_header = "Blogz", authors = authors)
    
@app.route("/blog", methods=['GET'])
def blogs():
    
    blog_id = request.args.get('id')
    author_id = request.args.get('user')
    author_name = request.args.get('username')

    
    if blog_id:
        single_post = Blog.query.filter_by(id = blog_id).all()
        return render_template('main.html', pagetitle ="Blog Posts", main_header = "Blogz", blogs = single_post)
    
    
    if author_id:
        author_posts = Blog.query.filter_by(author_id = author_id).all()
        author_header = "Blog Posts by " + author_name
        return render_template('main.html', pagetitle="Blog Posts", main_header = author_header, blogs=author_posts)
    
       
    blogs = Blog.query.all()
    main_header = "Welcome to the PURPLE!"
    return render_template('main.html', pagetitle = "Blog Posts", main_header = main_header, blogs = blogs)

@app.route("/login", methods=['GET','POST'])
def login():
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_login = User.query.filter_by(username=username).first()
       
        if user_login and user_login.password == password:
            session['username'] = username
            flash('You are now logged in', 'ok_to_go')
            return redirect('/newpost')
           
        flash('The username or password you entered did not match our system, please try again', 'error')
    return render_template('login.html')

@app.route("/logout", methods=['GET'])
def logout():
    del session['username']
    flash('You have been logged out', 'ok_to_go')
    return redirect('/blog')

@app.route('/signup', methods=['GET','POST'])
def signup():
    
    if request.method == 'POST':
        
        username = request.form['username']
        password = request.form['pass1']
        verify = request.form['pass2']
        
        existing_user = User.query.filter_by(username = username).first()
        total_errors = 0

        if username == '' or password == '' or verify == '':
            flash('Sorry, one or more fields are invalid.  A username, password, and password verification are required.', 'error')
            total_errors += 1
        if valid_input(username) == False:
            flash('Sorry, that username won\'t work!  Please enter a username between 3 and 40 characters, with no spaces.', 'error')
            total_errors += 1
        if valid_input(password) == False:
            flash('Sorry, that password won\'t work!  Please enter a password between 3 and 40 characters, with no spaces.', 'error')
            total_errors += 1    
        if verify_pass(password, verify) == False:
            flash('These passwords don\'t match!  Please enter your passwords again.', 'error')
            total_errors += 1
        if existing_user:
            flash('This username is already taken. If you would like to sign in as this user, click <a href=\'/login\'>here.</a>', 'error')
            total_errors += 1
        
        if total_errors > 0:
            return render_template('signup.html')

        if total_errors == 0:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()

            session['username'] = username
            return redirect('/newpost')


    return render_template('signup.html')

@app.route('/newpost', methods = ['GET', 'POST'])
def new_post():
    
    if request.method == 'POST':

        blog_title = request.form['title']
        blog_content = request.form['blogpost']  
        author_id = User.query.filter_by(username=session['username']).first()
                
        if blog_title == '' or blog_content == '':
            if blog_title == '':
                flash("Please enter a title for this blog post!", 'error')
            if blog_content == '':
                flash("Please add content to the body of your post!", 'error')
           
            return render_template('newpost.html', pagetitle="Add a Blog Post", title = blog_title, blogpost = blog_content)
        
        
        new_post = Blog(blog_title, blog_content, author_id)
        db.session.add(new_post)
        db.session.commit()  
                
        return redirect('/blog?id=' + str(new_post.id))
     
    return render_template('newpost.html', pagetitle = "Add a Blog Post")  


if __name__ == '__main__':
    app.run()