from flask import render_template, request, redirect, url_for
from app import app
from ghapi.all import GhApi
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
import pandas as pd

bson_types = [
    "String",
    "Integer",
    "Double",
    "Boolean",
    "Date",
    "ObjectId",
    "Array",
    "Binary Data",
    "Undefined",
    "Object",
    "Null",
    "Regular Expression",
    "JavaScript",
    "Symbol",
    "JavaScript with Scope",
    "32-bit Integer",
    "Timestamp",
    "64-bit Integer",
    "Decimal128",
    "Min Key",
    "Max Key"
]



# Load MongoDB credentials from environment variables
mongodb_username = os.environ.get('MONGODB_USERNAME')
mongodb_password = os.environ.get('MONGODB_PASSWORD')

# MongoDB connection URI
uri = f"mongodb+srv://{mongodb_username}:{mongodb_password}@cluster0.c80whlg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['projectdatabase']

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

@app.route('/')
def index():
    projects = db.projects.find()
    
    df = pd.DataFrame(list(projects))
    
    table_columns = df.columns.tolist()
    print(table_columns)

    table_rows = df.to_dict(orient='records')
    print(table_rows)

    return render_template('index.html', table_columns=table_columns, table_rows=table_rows)


@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        name = request.form['title']
        aanleiding = request.form['aanleiding']
        doelstelling = request.form['doelstelling']
        beoogd_resultaat = request.form['beoogd_resultaat']
        private = True
        auto_init = True

        gh = GhApi(token=os.environ.get('GH_TOKEN2'))
        org = 'DIClutter'

        repos = gh.repos.list_for_org(org)
        if any(repo.name == name for repo in repos):
            error_message = f"Repository '{name}' already exists in the organization."
            return render_template('error.html', error_message=error_message)

        gh.repos.create_in_org(org, name=name, description=beoogd_resultaat, private=private, auto_init=auto_init)

        db.projects.insert_one({'title': name, 'beoogd_resultaat': beoogd_resultaat, 'aanleiding': aanleiding, 'doelstelling': doelstelling})

        return redirect(url_for('index'))
    else:
        return render_template('create.html')

@app.route('/edit/<string:id>', methods=['GET', 'POST'])
def edit(id):
    project = db.projects.find_one({'_id': ObjectId(id)})
    if request.method == 'POST':
        db.projects.update_one({'_id': ObjectId(id)}, {'$set': {'title': request.form['title'], 'beoogd_resultaat': request.form['beoogd_resultaat'], 'aanleiding' : request.form['aanleiding'], 'doelstelling' : request.form['doelstelling']}})
        return redirect(url_for('index'))
    else:
        return render_template('edit.html', project=project)

@app.route('/delete/<string:id>', methods=['POST'])
def delete(id):
    db.projects.delete_one({'_id': ObjectId(id)})
    return redirect(url_for('index'))


@app.route('/configuration')
def configuration():
    configurations = db.configurations.find()

    df = pd.DataFrame(list(configurations))
    
    table_columns = df.columns.tolist()
    print(table_columns)

    table_rows = df.to_dict(orient='records')
    print(table_rows)

    return render_template('configuration.html', table_columns=table_columns, table_rows=table_rows)


@app.route('/makeconfig', methods=['GET', 'POST'])
def makeconfig():
    if request.method == "POST":
        attribute_name = request.form["attributename"]
        attribute_type = request.form["attributetype"]
        db.configurations.insert_one({'name': attribute_name, 'type': attribute_type})
        return redirect(url_for('configuration'))
    else:
        return render_template('makeconfig.html', bson_types=bson_types)
    

@app.route('/editconfig/<string:id>', methods=['GET', 'POST'])
def editconfig(id):
    configuration = db.configurations.find_one({'_id': ObjectId(id)})
    if request.method == 'POST':
        return redirect(url_for('configuration'))
    else:
        return render_template('edit.html', configuration=configuration)

@app.route('/deleteconfig/<string:id>', methods=['POST'])
def deleteconfig(id):
    db.configurations.delete_one({'_id': ObjectId(id)})
    return redirect(url_for('configuration'))


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