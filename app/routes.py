from flask import render_template, request, redirect, url_for
from app import app
from ghapi.all import GhApi
import os
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['projectdatabase']

@app.route('/')
def index():
    projects = db.projects.find()
    return render_template('index.html', projects=projects)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        name = request.form['title'] 
        description = request.form['description']
        private = True  
        auto_init = True  

        gh = GhApi(token=os.environ.get('GH_TOKEN2'))
        org = 'DIClutter' 
        gh.repos.create_in_org(org, name=name, description=description, private=private, auto_init=auto_init)

        db.projects.insert_one({'title': name, 'description': description})

        return redirect(url_for('index'))
    else:
        return render_template('create.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    project = db.projects.find_one({'_id': id})
    if request.method == 'POST':
        db.projects.update_one({'_id': id}, {'$set': {'title': request.form['title'], 'description': request.form['description']}})
        return redirect(url_for('index'))
    else:
        return render_template('edit.html', project=project)

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    db.projects.delete_one({'_id': id})
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
