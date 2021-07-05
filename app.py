
import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
from flask_kerberos import init_kerberos
from flask_kerberos import requires_authentication
from random import randrange

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_user(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM usersdb WHERE id = ?',
                        (user_id,)).fetchone()
    conn.close()
    if user is None:
        abort(404)
    return user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'notasecret'


@app.route('/')
def index():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM usersdb').fetchall()
    conn.close()
    return render_template('index.html', users=users)

@app.route('/<int:user_id>')
def user(user_id):
    user = get_user(user_id)
    return render_template('user.html', user=user)

@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        username = request.form['name']
        userrole = request.form['role']

        if not username:
            flash('Name is required!')
        elif not userrole:
            flash('Role is required!')
        else:
            N = 1
            usertoken = username + userrole + str(randrange(100000))
            print("usertoken ", usertoken)
            conn = get_db_connection()
            conn.execute('INSERT INTO usersdb (username, userrole, usertoken) VALUES (?, ?, ?)',
                         (username, userrole, usertoken))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    return render_template('create.html')

@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    user = get_user(id)
    print("user", user) 
    if request.method == 'POST':
        print("request.form ", request.form)
        username = request.form['name']
        userrole = request.form['role']
        print(username, userrole, id)

        if not username:
            flash('Name is required!')
        elif not userrole:
            flash('Role is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE usersdb SET username = ?, userrole = ?'
                         ' WHERE id = ?',
                         (username, userrole, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit.html', user=user)

@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    user = get_user(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM usersdb WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(user['username']))
    return redirect(url_for('index'))



# kerberos
@app.route("/protected")
@requires_authentication
def protected_view(user):
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM usersdb').fetchall()
    conn.close()
    return render_template('index.html', users=users)

# @app.route("/")
# @requires_authentication
# def index(user):
#     return render_template('index.html', user=user)


if __name__ == '__main__':
    init_kerberos(app)
    app.run(host='0.0.0.0')