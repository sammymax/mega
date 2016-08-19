from flask import Flask, jsonify, request, g, redirect
import os
import json
import sqlite3
from PIL import Image
from string import digits, ascii_lowercase, ascii_uppercase
from subprocess import Popen
import traceback

application = Flask(__name__)
application.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

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
    team, cookie = request.form.get('domain'), request.form.get('cookie')
    if f is None or not allowedFile(f.filename):
        return 'Bad file'
    name = os.path.splitext(f.filename)[0]
    if os.path.isdir(name):
        return 'Error: emoji with same name currently processing'
    os.mkdir(name)
    f.save(name + '/' + f.filename)

    dim = Image.open(name + '/' + f.filename).size
    sz, w, h = getsz(dim[0], dim[1])
    get_db().cursor().execute('INSERT INTO dims VALUES (?,?,?,?)', [team, name, w//sz, h//sz])
    get_db().commit()

    Popen(["python", "cut.py", name, team, cookie, str(sz), str(w), str(h)])
    return 'File upload successful'

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

def allowedFile(name):
    return '.' in name and name.rsplit('.', 1)[1] in set(['gif'])

def getsz(w, h):
    minpad = 10000000
    bestSz = 25
    # i : how many we tile with
    for i in range(25,75):
        rw = i * ((w + i - 1) // i)
        rh = i * ((h + i - 1) // i)
        if rw*rh - w*h <= minpad:
            minpad = rw*rh - w*h
            bestSz = i
    rw = bestSz * ((w + bestSz - 1) // bestSz)
    rh = bestSz * ((h + bestSz - 1) // bestSz)
    return (bestSz, rw, rh)

if __name__ == '__main__':
    print('Starting server...')
    application.run(host='0.0.0.0')
