from flask import render_template, request, redirect, url_for
from app import app
import sqlite3
from ghapi.all import GhApi
import os
import shutil
from datetime import datetime


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

def backup_database():
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_filename = f"projectdatabase_backup_{current_time}.db"
    shutil.copy("projectdatabase.db", backup_filename)


sqlite_data_types = [
    'INTEGER',
    'REAL',
    'TEXT',
    'BLOB',
    'NUMERIC'
]


@app.route('/')
def index():
    conn = get_db_connection()
    projects = conn.execute('SELECT * FROM projects').fetchall()
    conn.close()
    return render_template('index.html', projects=projects)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        # Handle form submission to create a new project
        title = request.form['title']
        description = request.form['description']
        
        # Get the column names from the projects table
        conn = get_db_connection()
        cursor = conn.execute('PRAGMA table_info(projects)')
        column_names = [row[1] for row in cursor.fetchall()]
        
        # Prepare new values for insertion, setting the first column (ID) to NULL
        new_values = [None] + [request.form.get(col, '') for col in column_names[1:]]
        
        # Generate placeholders string based on the number of columns
        placeholders = ', '.join(['?' for _ in range(len(column_names))])
        
        # Insert the new project into the database
        conn.execute(f'INSERT INTO projects VALUES ({placeholders})', new_values)
        conn.commit()
        conn.close()
        
        return redirect(url_for('index'))
    else:
        # Pass column names to the template
        conn = get_db_connection()
        cursor = conn.execute('PRAGMA table_info(projects)')
        column_names = [row[1] for row in cursor.fetchall()]
        conn.close()
        
        return render_template('create.html', column_names=column_names)



@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db_connection()
    project = conn.execute('SELECT * FROM projects WHERE id = ?', (id,)).fetchone()
    
    if request.method == 'POST':
        # Handle form submission to edit an existing project
        new_values = [request.form.get(col, '') for col in project.keys()]
        
        # Update the project in the database
        conn.execute('UPDATE projects SET title = ?, description = ? WHERE id = ?',
                     [new_values[1], new_values[2], id])
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


@app.route('/edit_table')
def edit_table():
    # Fetch existing columns from the table
    conn = sqlite3.connect('projectdatabase.db')
    cursor = conn.cursor()
    cursor.execute('PRAGMA table_info(projects)')
    columns = cursor.fetchall()
    conn.close()
    return render_template('edit_table.html', columns=columns)

@app.route('/edit_column/<column_name>', methods=['GET', 'POST'])
def edit_column(column_name):
    if request.method == 'POST':
        backup_database()
        new_column_name = request.form['new_column_name']
        new_data_type = request.form['new_data_type']
        # Update column in the table
        conn = sqlite3.connect('projectdatabase.db')
        cursor = conn.cursor()
        cursor.execute(f'ALTER TABLE projects RENAME COLUMN {column_name} TO {new_column_name}')
        cursor.execute(f'ALTER TABLE projects ALTER COLUMN {new_column_name} TYPE {new_data_type}')
        conn.commit()
        conn.close()
        return redirect(url_for('edit_table'))
    else:
        return render_template('edit_column.html', column_name=column_name, sqlite_data_types=sqlite_data_types)

@app.route('/delete_column/<column_name>', methods=['POST'])
def delete_column(column_name):
    # Delete column from the table
    backup_database()
    conn = sqlite3.connect('projectdatabase.db')
    cursor = conn.cursor()
    cursor.execute(f'ALTER TABLE projects DROP COLUMN {column_name}')
    conn.commit()
    conn.close()
    return redirect(url_for('edit_table'))

@app.route('/add_column', methods=['GET', 'POST'])
def add_column():
    if request.method == 'POST':
        backup_database()
        new_column_name = request.form['new_column_name']
        new_data_type = request.form['new_data_type']
        # Add new column to the table
        conn = sqlite3.connect('projectdatabase.db')
        cursor = conn.cursor()
        cursor.execute(f'ALTER TABLE projects ADD COLUMN {new_column_name} {new_data_type}')
        conn.commit()
        conn.close()
        return redirect(url_for('edit_table'))
    else:
        return render_template('add_column.html', sqlite_data_types=sqlite_data_types)