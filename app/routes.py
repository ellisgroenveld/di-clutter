from flask import render_template, request, redirect, url_for
from app import app
import sqlite3
from ghapi.all import GhApi
import os

def get_db_connection():
    conn = sqlite3.connect('projectdatabase.db')
    conn.row_factory = sqlite3.Row
    conn.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL
        )
    ''')
    return conn


@app.route('/')
def index():
    conn = get_db_connection()
    projects = conn.execute('SELECT * FROM projects').fetchall()
    conn.close()
    return render_template('index.html', projects=projects)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        conn = get_db_connection()
        name = request.form['title'] 
        description = request.form['description']
        private = True  
        auto_init = True  

        
        gh = GhApi(token=os.environ.get('GH_TOKEN2'))
        org = 'DIClutter' 
        gh.repos.create_in_org(org, name=name, description=description, private=private, auto_init=auto_init)

        conn.execute('INSERT INTO projects (title, description) VALUES (?, ?)',
                     [name, description])
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    else:
        return render_template('create.html')



@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db_connection()
    project = conn.execute('SELECT * FROM projects WHERE id = ?', (id,)).fetchone()
    conn.close()
    if request.method == 'POST':
        conn = get_db_connection()
        conn.execute('UPDATE projects SET title = ?, description = ? WHERE id = ?',
                     [request.form['title'], request.form['description'], id])
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    else:
        return render_template('edit.html', project=project)

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM projects WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/githubrepos')
def github_repos():
    gh = GhApi()

    token = os.environ.get('GH_TOKEN2')

    gh = GhApi(token=token)

    org = 'DIClutter'

    repos = gh.repos.list_for_org(org)

    for repo in repos:
        contributors = gh.repos.list_contributors(owner=org, repo=repo.name)
        repo.contributors = [contributor.login for contributor in contributors]

    return render_template('githubrepos.html', repos=repos)
