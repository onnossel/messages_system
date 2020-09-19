

def insert_new_message(conn, message):
    sql = ''' INSERT INTO messages(username,sender,subject,body,date,read)
              VALUES(?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, message)
    conn.commit()
    return cur.lastrowid


def insert_new_user(conn, user):
    sql = ''' INSERT INTO users(username,password)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, user)
    conn.commit()
    return cur.lastrowid


def get_message_by_id(conn, id):
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM messages WHERE id=?", (id,))
        rows = cur.fetchall()
        message = {
            'id': rows[0][0],
            'user': rows[0][1],
            'from': rows[0][2],
            'subject': rows[0][3],
            'body': rows[0][4],
            'date': rows[0][5]
        }
    except:
        return "ID does not exist\n" \
               "Please see /get_all_messages for choosing the right ID"
    cur.execute("UPDATE messages SET read = 1 WHERE id = ?", (id,))
    conn.commit()
    return message


def get_messages_by_user(conn, username, unread=None):
    cur = conn.cursor()

    if unread:
        cur.execute("SELECT * FROM messages WHERE username=? AND read=?", (username, False,))
    else:
        cur.execute("SELECT * FROM messages WHERE username=?", (username,))
    rows = cur.fetchall()
    messages = []
    for i in range(0, len(rows)):
        message = {
            'id': rows[i][0],
            'user': rows[i][1],
            'from': rows[i][2],
            'subject': rows[i][3],
            'body': rows[i][4],
            'date': rows[i][5]
        }
        messages.append(message)
    cur.execute("UPDATE messages SET read = 1 WHERE username = ?", (username,))
    conn.commit()
    return messages


def delete_message_by_id(conn, id):
    sql = 'DELETE FROM messages WHERE id=?'
    cur = conn.cursor()
    cur.execute(sql, (id,))
    conn.commit()