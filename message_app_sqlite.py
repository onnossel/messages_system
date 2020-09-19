from flask import Flask, request, jsonify, session
from utils_funcs import get_messages_by_user, get_message_by_id, insert_new_message, insert_new_user, delete_message_by_id
import sqlite3
import datetime


app = Flask(__name__)
app.secret_key = '12345'

# Set connection to sqlite
conn = sqlite3.connect('message_box.db')
cur = conn.cursor()
# Create Tables if not alredy exists
cur.execute("""CREATE TABLE IF NOT EXISTS messages(
   id integer PRIMARY KEY,
   username text,
   sender text,
   subject text,
   body TEXT,
   date INTEGER,
   read TEXT);
""")
cur.execute("""CREATE TABLE IF NOT EXISTS users(
   username TEXT PRIMARY KEY,
   password INTEGER);
""")
conn.commit()


@app.route('/', methods=['GET','POST'])
def home():
    return 'This is home route'


@app.route('/sign_up', methods=['POST'])
def sign_up():
    if request.is_json:
        try:
            content = request.get_json()
            user = content['user']
            password = content['password']
        except:
            return 'There was a problem with the content', 400
        try:
            # Initialize a new user object
            new_user = (user,password)
            # Insert one new user to the db
            conn = sqlite3.connect('message_box.db')
            insert_new_user(conn,new_user)
            return 'User {} has been created\n' \
                   'To login please visit /login'.format(user)
        except Exception as e:
            return 'An error occured - \n' + str(e), 500


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            # Find user details in the db
            conn = sqlite3.connect('message_box.db')
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE username=?", (request.form['username'],))
            result = cur.fetchall()
            if not result:
                return 'You were unable to login. There can be a few reasons:\n' \
                       '1. You have entered an incorrect username\n' \
                       '2. You did not sign up\n' \
                       'Please sign up at /sign_up or make sure your username is correct to continue'
            user = result[0][0]
            password = result[0][1]
            if request.form['password'] != str(password):
                return 'You have entered a wrong password'
            # Keep track of logged in user
            session['user'] = user
            return 'You are signed in as {}'.format(user)
        except Exception as e:
            return 'An error occured - \n' + str(e), 500


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('logged_in', None)


@app.route("/write_message", methods=['POST'])
def write_message():
    if request.is_json:
        try:
            content = request.get_json()
            sender = content['sender']
            reciver = content['reciver']
            subject = content['subject']
            body = content['body']
            today = datetime.datetime.today()
        except:
            return 'There was a problem with the content', 400
        try:
            # Initialize a single message object as Dict
            message = (reciver, sender, subject, body, today.strftime('%d%m%Y'), False)
            # Insert one message to the db
            conn = sqlite3.connect('message_box.db')
            insert_new_message(conn,message)
            return 'Message sent to user {}'.format(reciver), 201
        except Exception as e:
            return 'An error occured - \n' + str(e), 500


@app.route("/get_message/<int:id>", methods=['GET'])
def get_message(id=None):
        try:
            # Find message by id
            conn = sqlite3.connect('message_box.db')
            result = get_message_by_id(conn, id)
            return result
        except Exception as e:
            return 'An error occured - \n' + str(e), 500


@app.route("/get_all_messages", methods=['GET'])
@app.route("/get_all_messages/<user>", methods=['GET'])
def get_all_messages(user=None):
    # handling logged in user
    if not user:
        try:
            # Find all messages for logged in user
            conn = sqlite3.connect('message_box.db')
            result = get_messages_by_user(conn, session['user'])
            return jsonify(result)
        except:
            return 'Please enter user or login', 400
    try:
        # Find all messages for specified user
        conn = sqlite3.connect('message_box.db')
        result = get_messages_by_user(conn, user)
        return jsonify(result)
    except Exception as e:
        return 'An error occured - \n' + str(e), 500


@app.route("/get_unread_messages", methods=['GET'])
@app.route("/get_unread_messages/<user>", methods=['GET'])
def get_unread_messages(user=None):
    # Handling a logged in user
    if not user:
        try:
            # Find all unread messages for logged in user
            conn = sqlite3.connect('message_box.db')
            result = get_messages_by_user(conn, session['user'], unread=True)
            return jsonify(result)
        except:
            return 'Please enter user or login', 400
    try:
        # Find all unread messages for specified user
        conn = sqlite3.connect('message_box.db')
        result = get_messages_by_user(conn, user, unread=True)
        return jsonify(result)
    except Exception as e:
        return 'An error occured - \n' + str(e), 500


@app.route("/delete_message/<int:id>", methods=['DELETE'])
def delete_message(id):
    try:
        # Delete message by id
        conn = sqlite3.connect('message_box.db')
        delete_message_by_id(conn, id)
        return 'Message {} was deleted'.format(id)
    except Exception as e:
        return 'An error occured - \n' + str(e), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='3000')
