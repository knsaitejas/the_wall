from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import re
import md5
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
mysql = MySQLConnector(app,'mydb')
app.secret_key = "thisisthebestkeyeveromgwhyisitsoamazingitissocool"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/register', methods=['POST'])
def register():
    if len(request.form['first_name']) < 3:
        flash('PLEASE ENTER FULL NAME')
    elif len(request.form['last_name']) < 3:
        flash('PLEASE ENTER FULL LAST NAME') 
    elif not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid Email Address!")  
    elif request.form['password'] != request.form['password2']:
        flash('PLEASE MAKE SURE PASSWORDS MATCH')
    else:
        data = {
            'First_Name': request.form['first_name'],
            'Last_Name': request.form['last_name'],
            'Email': request.form['email'],
            'Password': md5.new(request.form['password']).hexdigest()
        }
        query = 'INSERT INTO users(first_name, last_name, email, password) VALUES (:First_Name, :Last_Name, :Email, :Password)'

        mysql.query_db(query, data)
    return redirect('/')

@app.route('/login', methods=["POST"])   
def login():
    if not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid Email Address!")  
    elif len(request.form['password']) < 1:
        flash('enter password pls')   
    else:
        data = {
            'email': request.form['email'],
            'Password': md5.new(request.form['password']).hexdigest()
        } 
        query = 'SELECT email FROM users WHERE users.email = :email'
        if mysql.query_db(query, data) == []:
            flash('you are not a user')
            return redirect('/')
        email=(mysql.query_db(query, data))[0]['email'] 
        query = 'SELECT password FROM users WHERE users.email = :email'
        password=(mysql.query_db(query, data))[0]['password'] 
        query = 'SELECT id FROM users WHERE users.email = :email'
        session['id'] = (mysql.query_db(query, data))[0]['id']
        # print session['id']
        if request.form['email'] == email and password == md5.new(request.form['password']).hexdigest():
            return redirect('/wall')
        elif password != md5.new(request.form['password']).hexdigest():
            flash('username OR password is WRONG')
        elif email_check == []:
            flash('you fucked up')
    return redirect('/')

@app.route('/wall')   
def wall():
    data = {
        'id': session['id']
    }
    query='SELECT first_name FROM users WHERE users.id = :id'
    session['name'] = (mysql.query_db(query, data))[0]['first_name']
    query='SELECT * FROM messages LEFT JOIN users ON users.id = messages.users_id ORDER BY messages.created_at DESC'
    user_messages = mysql.query_db(query,data)
    query = 'SELECT * FROM comments LEFT JOIN users ON users.id = comments.users_id LEFT JOIN messages ON messages.m_id = comments.messages_id ORDER BY comments.created_at ASC'
    user_comments = mysql.query_db(query,data)
    # print user_messages
    print user_comments
    return render_template('wall.html', name=session['name'],user_messages=user_messages, user_comments=user_comments)

@app.route('/posted', methods=['POST'])  
def posted():
    data = {
        'message': str(request.form['message']),
        'users_id': int(session['id'])
    }
    query='INSERT INTO messages (users_id, message) VALUES (:users_id, :message)'
    mysql.query_db(query,data)
    return redirect('/wall')

@app.route('/commented', methods=['POST'])
def commented():
    data = {
        'comment': str(request.form['comment']),
        'users_id': int(session['id']),
        'messages_id': int(request.form['message_id'])
    }
    query = 'INSERT INTO comments (users_id, messages_id, comment) VALUES (:users_id, :messages_id, :comment)'
    mysql.query_db(query,data)
    return redirect('/wall')


app.run(debug=True)