from flask import Flask, request, jsonify, session
from pymongo import MongoClient
import datetime


app = Flask(__name__)
app.secret_key = '12345'

# Set connection to mongoDB
client = MongoClient()
db = client.messagebox
# Set global collections
USERS_COLLECTION = db.users
MESSAGES_COLLECTION = db.messages


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
            # Initialize a new user object as Dict
            new_user = {
                'user': user,
                'password': password
            }
            # Insert one new user to the db
            result = USERS_COLLECTION.insert_one(new_user)
            return 'User {} has been created\n' \
                   'User id is - {}\n' \
                   'To login please visit /login'.format(user, result.inserted_id)
        except Exception as e:
            return 'An error occured - \n' + str(e), 500


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            # Find user details in the db
            result = USERS_COLLECTION.find_one({'user': request.form['username']})
            if not result:
                return 'You were unable to login. There can be a few reasons:\n' \
                       '1. You have entered an incorrect username\n' \
                       '2. You did not sign up\n' \
                       'Please sign up at /sign_up or make sure your username is correct to continue'
            user = result['user']
            password = result['password']
            if request.form['password'] != password:
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
            message = {
                'user': reciver,
                'from': sender,
                'subject': subject,
                'body': body,
                'date': today.strftime('%d%m%Y'),
                'read': False
            }
            # Insert one message to the db
            MESSAGES_COLLECTION.insert_one(message)
            return 'Message sent to user {}'.format(reciver), 201
        except Exception as e:
            return 'An error occured - \n' + str(e), 500


@app.route("/get_message", methods=['GET'])
@app.route("/get_message/<user>", methods=['GET'])
def get_message(user=None):
        # handling logged in user
        if not user:
            try:
                # Find all messages for logged in user and update all unread messages to read
                result = MESSAGES_COLLECTION.find_one_and_update({'user': session['user']}, {"$set": {"read": True}}, {'_id': False})
                return result
            except:
                return 'Please enter user or login', 400
        try:
            # Find all messages for specified user and update all unread messages to read
            result = MESSAGES_COLLECTION.find_one_and_update({'user': user}, {"$set": {"read": True}}, {'_id': False})
            return result
        except Exception as e:
            return 'An error occured - \n' + str(e), 500


@app.route("/get_all_messages", methods=['GET'])
@app.route("/get_all_messages/<user>", methods=['GET'])
def get_all_messages(user=None):
    messages = []
    # handling logged in user
    if not user:
        try:
            # Find all messages for logged in user
            result = MESSAGES_COLLECTION.find({'user': session['user']}, {'_id': False})
            # Update all unread messages to read
            MESSAGES_COLLECTION.update_many({'user': session['user']}, {"$set": {"read": True}})
            for message in result:
                messages.append(message)
            return jsonify(messages)
        except:
            return 'Please enter user or login', 400
    try:
        # Find all messages for specified user
        result = MESSAGES_COLLECTION.find({'user': user}, {'_id': False})
        # Update all unread messages to read
        MESSAGES_COLLECTION.update_many({'user': user}, {"$set": {"read": True}})
        for message in result:
            messages.append(message)
        return jsonify(messages)
    except Exception as e:
        return 'An error occured - \n' + str(e), 500


@app.route("/get_unread_messages", methods=['GET'])
@app.route("/get_unread_messages/<user>", methods=['GET'])
def get_unread_messages(user=None):
    messages = []
    # Handling a logged in user
    if not user:
        try:
            # Find all unread messages for logged in user
            result = MESSAGES_COLLECTION.find({"$and": [{'user': session['user']}, {'read': False}]}, {'_id': False})
            for message in result:
                messages.append(message)
            # Update all unread messages to read
            MESSAGES_COLLECTION.update_many({"$and": [{'user': session['user']}, {'read': False}]}, {"$set": {"read": True}})
            return jsonify(messages)
        except:
            return 'Please enter user or login', 400
    try:
        # Find all unread messages for specified user
        result = MESSAGES_COLLECTION.find({"$and" : [{'user': user}, {'read': False}]}, {'_id': False})
        for message in result:
            messages.append(message)
        # Update all unread messages to read
        MESSAGES_COLLECTION.update_many({"$and": [{'user': user}, {'read': False}]}, {"$set": {"read": True}})
        return jsonify(messages)
    except Exception as e:
        return 'An error occured - \n' + str(e), 500


@app.route("/delete_message/<user>", methods=['DELETE'])
def delete_message(user):
    try:
        MESSAGES_COLLECTION.find_one_and_delete({'user': user}, {'_id': False})
        return 'Message deleted to user {}'.format(user)
    except Exception as e:
        return 'An error occured - \n' + str(e), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='3000')
