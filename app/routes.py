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
    "Null"
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

    table_rows = df.to_dict(orient='records')

    return render_template('index.html', table_columns=table_columns, table_rows=table_rows)


@app.route('/create', methods=['GET', 'POST'])
def create():
    configurations = db.configurations.find({'inuse': True})  # Fetch configurations where inuse=True
    if request.method == 'POST':
        name = request.form['title']
        aanleiding = request.form['aanleiding']
        doelstelling = request.form['doelstelling']
        beoogd_resultaat = request.form['beoogd_resultaat']
        
        # Iterate over configurations to dynamically collect form data
        dynamic_fields = {}
        for config in configurations:
            attribute_name = config['name']
            attribute_type = config['type']
            if attribute_type == 'String':
                dynamic_fields[attribute_name] = request.form[attribute_name]
            elif attribute_type == 'Integer':
                dynamic_fields[attribute_name] = int(request.form[attribute_name])
            elif attribute_type == 'Double':
                dynamic_fields[attribute_name] = float(request.form[attribute_name])
            elif attribute_type == 'Boolean':
                dynamic_fields[attribute_name] = bool(request.form.get(attribute_name))
            elif attribute_type == 'Date':
                dynamic_fields[attribute_name] = request.form[attribute_name]
            elif attribute_type == 'ObjectId':
                dynamic_fields[attribute_name] = ObjectId(request.form[attribute_name])
            elif attribute_type == 'Array':
                dynamic_fields[attribute_name] = request.form.getlist(attribute_name)
            elif attribute_type == 'Binary Data':
                dynamic_fields[attribute_name] = request.files[attribute_name].read()
            elif attribute_type == 'Undefined':
                dynamic_fields[attribute_name] = None
            elif attribute_type == 'Null':
                dynamic_fields[attribute_name] = None
            
        private = True
        auto_init = True

        gh = GhApi(token=os.environ.get('GH_TOKEN2'))
        org = 'DIClutter'

        repos = gh.repos.list_for_org(org)
        if any(repo.name == name for repo in repos):
            error_message = f"Repository '{name}' already exists in the organization."
            return render_template('error.html', error_message=error_message)

        gh.repos.create_in_org(org, name=name, description=beoogd_resultaat, private=private, auto_init=auto_init)

        db.projects.insert_one({'title': name, 'beoogd_resultaat': beoogd_resultaat, 'aanleiding': aanleiding, 'doelstelling': doelstelling, **dynamic_fields})

        return redirect(url_for('index'))
    else:
        return render_template('create.html', configurations=configurations)


@app.route('/edit_project/<string:id>', methods=['GET', 'POST'])
def edit_project(id):
    project = db.projects.find_one({'_id': ObjectId(id)})
    configurations = db.configurations.find()  # Fetch all configurations
    if request.method == 'POST':
        # Iterate over configurations to dynamically collect form data
        dynamic_fields = {}
        for config in configurations:
            attribute_name = config['name']
            if attribute_name in project:
                attribute_type = config['type']
                if attribute_type in ['String', 'Integer', 'Double', 'Boolean', 'Date', 'ObjectId', 'Array', 'Binary Data', 'Undefined', 'Null']:
                    dynamic_fields[attribute_name] = request.form.get(attribute_name)
        db.projects.update_one({'_id': ObjectId(id)}, {'$set': dynamic_fields})
        return redirect(url_for('index'))
    else:
        return render_template('edit_project.html', project=project, configurations=configurations)



@app.route('/delete/<string:id>', methods=['POST'])
def delete(id):
    db.projects.delete_one({'_id': ObjectId(id)})
    return redirect(url_for('index'))


@app.route('/configuration')
def configuration():
    configurations = db.configurations.find()

    df = pd.DataFrame(list(configurations))
    
    table_columns = df.columns.tolist()

    table_rows = df.to_dict(orient='records')

    return render_template('configuration.html', table_columns=table_columns, table_rows=table_rows)


@app.route('/makeconfig', methods=['GET', 'POST'])
def makeconfig():
    if request.method == "POST":
        attribute_name = request.form["attributename"]
        attribute_type = request.form["attributetype"]
        attribute_inuse = request.form.get("inuse", False)  # Get the value of inuse from the form
        # Convert attribute_inuse to boolean
        if attribute_inuse == "on":
            attribute_inuse = True
        else:
            attribute_inuse = False
        db.configurations.insert_one({'name': attribute_name, 'type': attribute_type, 'inuse': attribute_inuse})
        return redirect(url_for('configuration'))
    else:
        return render_template('makeconfig.html', bson_types=bson_types)


@app.route('/editconfig/<string:id>', methods=['GET', 'POST'])
def editconfig(id):
    configuration = db.configurations.find_one({'_id': ObjectId(id)})
    if request.method == 'POST':
        attribute_inuse = request.form.get("inuse", False)  # Get the value of inuse from the form
        # Convert attribute_inuse to boolean
        if attribute_inuse == "on":
            attribute_inuse = True
        else:
            attribute_inuse = False
        db.configurations.update_one({'_id': ObjectId(id)}, {'$set': {'name': request.form['attributename'], 'type': request.form['attributetype'], 'inuse' : attribute_inuse}})
        return redirect(url_for('configuration'))
    else:
        return render_template('editconfig.html', bson_types=bson_types, configuration=configuration)




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