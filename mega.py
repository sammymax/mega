from flask import Flask, jsonify, request, g
import os
import json
import sqlite3
from string import digits, ascii_lowercase, ascii_uppercase

application = Flask(__name__)

DATABASE = 'mega.db'
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db
@application.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@application.route('/mega/img', methods=['POST'])
def upload():
    f = request.files.get('file')
    if f is None:
        return 'No file'
    f.save("aaa.gif")

@application.route('/mega/slash', methods=['POST'])
def mega():
    team, token = request.form.get('team_domain'), request.form.get('token')
    cur = get_db().cursor()
    cur.execute('SELECT * FROM tokens WHERE team=?', [team])
    tokenRow = cur.fetchone()
    if tokenRow is None or tokenRow[1] != token:
        print("not in")
        return ''

    req = request.form['text'].split()
    if len(req) == 0:
        return jsonLines([':thinking_face:'])
    emoji = req[0]
    ops = '' if len(req) == 1 else req[1]

    cur.execute('SELECT * FROM dims WHERE team=? AND emoji=?', [team, emoji])
    dimRow = cur.fetchone()
    if dimRow != None:
        w, h = dimRow[2], dimRow[3]
        lines = []
        str62 = digits + ascii_lowercase + ascii_uppercase
        return jsonLines([''.join([':__{}__{}{}:'.format(emoji,str62[x],str62[y])
            for x in range(w)]) for y in range(h)])
    return jsonLines([':thinking_face:'])

def jsonLines(arr):
    txt = "\n".join(arr)
    return jsonify({"response_type" : "in_channel", "text" : txt})

if __name__ == '__main__':
    print('Starting server...')
    application.run(host='0.0.0.0')
