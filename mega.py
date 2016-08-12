from flask import Flask, jsonify, request, g, redirect
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

@application.route('/mega/reg', methods=['POST'])
def register():
    domain, token = request.form.get('domain'), request.form.get('token')
    if domain is None or token is None:
        return 'Invalid arguments'
    tokenRow = getTokenRow(domain)
    if tokenRow is not None:
        return 'Slack domain is already registered!'
    get_db().cursor().execute('INSERT INTO tokens VALUES (?,?)', [domain, token])
    get_db().commit()
    return 'Domain {} is now registered!'.format(domain)

@application.route('/mega/img', methods=['POST'])
def upload():
    f = request.files.get('file')
    if f is None:
        return 'No file'
    f.save("aaa.gif")

@application.route('/mega/slash', methods=['POST'])
def mega():
    team, token = request.form.get('team_domain'), request.form.get('token')
    tokenRow = getTokenRow(team)
    if tokenRow is None or tokenRow[1] != token:
        return 'Bad team/token combination'

    req = request.form['text'].split()
    if len(req) == 0:
        return jsonLines([':thinking_face:'])
    emoji = req[0]
    ops = '' if len(req) == 1 else req[1]

    cur = get_db().cursor()
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

def getTokenRow(team):
    cur = get_db().cursor()
    cur.execute('SELECT * FROM tokens WHERE team=?', [team])
    return cur.fetchone()

if __name__ == '__main__':
    print('Starting server...')
    application.run(host='0.0.0.0')
