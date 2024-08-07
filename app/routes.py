from flask import render_template, request, redirect, url_for, send_file, jsonify, abort
from app import app
from ghapi.all import GhApi
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import ReturnDocument
from bson.objectid import ObjectId
import pandas as pd
from email_validator import validate_email, EmailNotValidError
from urllib.parse import urlparse
from PIL import Image
import io
import zipfile
import math


if not os.path.exists('app/static/temp'):
    os.makedirs('app/static/temp')




bson_types = [
    "Array",
    "String",
    "Integer",
    "Double",
    "Boolean",
    "Date",
    "ObjectId",
    "Binary Data",
    "Undefined",
    "Null"
]

mongodb_uri = os.environ.get('MONGODB_URI')

# Create a new client and connect to the server
client = MongoClient(mongodb_uri)
db = client['projectdatabase']

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

def is_valid_email(email):
    try:
        # Validate the email address
        validate_email(email)
        return True
    except EmailNotValidError as e:
        # Email is not valid, return False
        return False

def convert_image_to_webp(image_stream):
    img = Image.open(image_stream)
    webp_io = io.BytesIO()
    img.save(webp_io, format='webp', quality=60)
    webp_io.seek(0)
    return webp_io.read()

def get_next_project_code():
    counter = db.counters.find_one_and_update(
        {'_id': 'project_id'},
        {'$inc': {'sequence_value': 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    return counter['sequence_value']

def get_next_overproject_code():
    counter = db.counters.find_one_and_update(
        {'_id': 'overproject_id'},
        {'$inc': {'sequence_value': 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    return counter['sequence_value']


def format_studentproject_number(number):
    if not (0 <= number < 10000):
        raise ValueError("Number must be between 0 and 9999")
    formatted_number = f"S-{number:04d}"
    return formatted_number


def format_overproject_number(number):
    if not (0 <= number < 10000):
        raise ValueError("Number must be between 0 and 9999")
    formatted_number = f"R-{number:04d}"
    return formatted_number



@app.route('/')
def index():
    return render_template('index.html')
    

@app.route('/projects')
def projects():
    projects = list(db.projects.find())
    overprojects = list(db.overkoepelende_projects.find())
    for project in projects:
        if 'overkoepelende_project' in project:
            overkoepelende_project = db.overkoepelende_projects.find_one({'_id': ObjectId(project['overkoepelende_project'])})
            project['overkoepelende_project'] = overkoepelende_project['research_project'] if overkoepelende_project else None

        if 'onderzoeker' in project:
            onderzoeker = db.onderzoekers.find_one({'_id': ObjectId(project['onderzoeker'])})
            project['onderzoeker'] = onderzoeker['name'] if onderzoeker else None

        if 'owe' in project:
            owe_obj = db.owe.find_one({'_id': ObjectId(project['owe'])})
            project['owe'] = owe_obj['name'] if owe_obj else None

        if 'project_image' in project and project['project_image']:
            with open('app/static/temp/' + str(project['_id']) + '.webp', 'wb') as f:
                f.write(project['project_image'])
            project['imagepath'] = str(project['_id']) + '.webp'

    df = pd.DataFrame(projects)
    table_columns = df.columns.tolist()
    table_rows = df.to_dict(orient='records')

    return render_template(
        'projects.html',
        table_columns=table_columns,
        table_rows=table_rows,
        overprojects=overprojects 
    )



@app.route('/create_project', methods=['GET', 'POST'])
def create_project():
    configurations = db.configurations.find({'inuse': True, 'ConnectedCollection': 'projects'})
    overkoepelende_projects = db.overkoepelende_projects.find()
    onderzoekers = db.onderzoekers.find()
    owe = db.owe.find()
    if request.method == 'POST':
        name = request.form['title']
        aanleiding = request.form['aanleiding']
        doelstelling = request.form['doelstelling']
        beoogd_resultaat = request.form['beoogd_resultaat']
        studentid = request.form['studentid']
        selected_overkoepelende_project = request.form['overkoepelende_project']
        selected_onderzoeker = request.form['onderzoeker']
        selected_owe = request.form['owe']

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
                dynamic_fields[attribute_name] = request.form[attribute_name]
            elif attribute_type == 'Binary Data':
                dynamic_fields[attribute_name] = request.files[attribute_name].read()
            elif attribute_type == 'Undefined':
                dynamic_fields[attribute_name] = None
            elif attribute_type == 'Null':
                dynamic_fields[attribute_name] = None
        project_image = request.files.get('project_image')
        image_binary = convert_image_to_webp(project_image.stream)

        project_code = format_studentproject_number(get_next_project_code())

        if request.form.get('githubenabled'): 
            private = True
            auto_init = True

            gh = GhApi(token=os.environ.get('GH_TOKEN2'))
            org = os.environ.get('GH_ORG')

            repos = gh.repos.list_for_org(org)
            if any(repo.name == name for repo in repos):
                error_message = f"Repository '{name}' already exists in the organization."
                return render_template('error.html', error_message=error_message)

            repo = gh.repos.create_in_org(org, name=name, description=beoogd_resultaat, private=private, auto_init=auto_init)

            db.projects.insert_one({'title': name, 'projectcode' : project_code,'aanleiding': aanleiding, 'doelstelling': doelstelling, 'beoogd_resultaat': beoogd_resultaat, 'studentid': studentid, 'githubrepo': repo.html_url, 'overkoepelende_project': selected_overkoepelende_project, 'onderzoeker': selected_onderzoeker, 'owe': selected_owe, 'project_image': image_binary, **dynamic_fields})
        else:
            githubrepo = request.form.get('githubrepo')
            db.projects.insert_one({'title': name, 'projectcode' : project_code,'aanleiding': aanleiding, 'doelstelling': doelstelling, 'beoogd_resultaat': beoogd_resultaat, 'studentid': studentid, 'githubrepo': githubrepo, 'overkoepelende_project': selected_overkoepelende_project, 'onderzoeker': selected_onderzoeker, 'owe': selected_owe, 'project_image': image_binary, **dynamic_fields})
        

        

        return redirect(url_for('projects'))
    else:
        return render_template('createproject.html', configurations=configurations, overkoepelende_projects=overkoepelende_projects, onderzoekers=onderzoekers, owe=owe)


@app.route('/edit_project/<string:id>', methods=['GET', 'POST'])
def edit_project(id):
    project = db.projects.find_one({'_id': ObjectId(id)})
    configurations = db.configurations.find({'inuse': True, 'ConnectedCollection': 'projects'})
    overkoepelende_projects = db.overkoepelende_projects.find()
    onderzoekers = db.onderzoekers.find()
    owe = db.owe.find()
    if request.method == 'POST':
        name = request.form['title']
        aanleiding = request.form['aanleiding']
        doelstelling = request.form['doelstelling']
        beoogd_resultaat = request.form['beoogd_resultaat']
        studentid = request.form['studentid']
        selected_overkoepelende_project = request.form['overkoepelende_project']
        selected_onderzoeker = request.form['onderzoeker']
        selected_owe = request.form['owe']
        githubrepo = request.form['githubrepo']
        
        # Remove ending slashes before saving. If we do not do this, the application will have issues later, because it finds the organization and reposituory based on seperating on slashes.
        try:
            if githubrepo[-1] == "/":
                githubrepo = githubrepo[:-1]
        except:
            pass

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
                dynamic_fields[attribute_name] = request.form[attribute_name]
            elif attribute_type == 'Binary Data':
                dynamic_fields[attribute_name] = request.files[attribute_name].read()
            elif attribute_type == 'Undefined':
                dynamic_fields[attribute_name] = None
            elif attribute_type == 'Null':
                dynamic_fields[attribute_name] = None

        db.projects.update_one({'_id': ObjectId(id)}, {'$set': {'title': name, 'beoogd_resultaat': beoogd_resultaat, 'aanleiding': aanleiding, 'doelstelling': doelstelling, 'studentid': studentid, 'githubrepo': githubrepo, 'overkoepelende_project': selected_overkoepelende_project, 'onderzoeker': selected_onderzoeker, 'owe': selected_owe, **dynamic_fields}})
        return redirect(url_for('projects'))
    else:
        return render_template('editproject.html', project=project, configurations=configurations, overkoepelende_projects=overkoepelende_projects, onderzoekers=onderzoekers, owe=owe)


@app.route('/delete_project/<string:id>', methods=['POST'])
def delete_project(id):
    project = db.projects.find_one({'_id': ObjectId(id)})
    if not project:
        return "Project not found", 404
    
    #COMMENT CODE BELOW IS USED TO DELETE A REPOSITORY WHEN DELETING A PROJECT. ITS VERY SUS.

    # github_repo_url = project.get('githubrepo')

    # if github_repo_url:
    #     parts = github_repo_url.split('/')
    #     owner = parts[-2]
    #     repo_name = parts[-1]

    #     token = os.environ.get('GH_TOKEN2')
    #     gh = GhApi(token=token)

    #     try:
    #         gh.repos.delete(owner=owner, repo=repo_name)
    #     except Exception as e:
    #         return f"Failed to delete repository from GitHub: {str(e)}", 500

    db.projects.delete_one({'_id': ObjectId(id)})

    return redirect(url_for('projects'))


@app.route('/project_details/<string:id>')
def project_details(id):
    project = db.projects.find_one({'_id': ObjectId(id)})
    
    if not project:
        # Handle case where project with given ID is not found
        abort(404)

    if 'project_image' in project and project['project_image']:
        with open('app/static/temp/' + str(project['_id']) + '.webp', 'wb') as f:
            f.write(project['project_image'])
        project['project_image'] = str(project['_id']) + '.webp'
    
    # Fetch related objects and add them to the project dictionary
    if 'overkoepelende_project' in project:
        overkoepelende_project = db.overkoepelende_projects.find_one({'_id': ObjectId(project['overkoepelende_project'])})
        project['overkoepelende_project'] = overkoepelende_project

    if 'onderzoeker' in project:
        onderzoeker = db.onderzoekers.find_one({'_id': ObjectId(project['onderzoeker'])})
        project['onderzoeker'] = onderzoeker

    if 'owe' in project:
        owe_obj = db.owe.find_one({'_id': ObjectId(project['owe'])})
        project['owe'] = owe_obj
    
    if 'githubrepo' in project:
        try:
            token = os.environ.get('GH_TOKEN2')
            gh = GhApi(token=token)
            
            github_url = project['githubrepo']
            owner, repo_name = github_url.split('/')[-2:]

            repo = gh.repos.get(owner=owner, repo=repo_name)

            contributors = gh.repos.list_contributors(owner=owner, repo=repo_name)
            contributors_list = [contributor.login for contributor in contributors]

            project['github_info'] = {
                'name': repo.name,
                'description': repo.description,
                'owner': repo.owner.login,
                'visibility': 'Private' if repo.private else 'Public',
                'language': repo.language,
                'contributors': contributors_list,
                'topics': ', '.join(repo.topics)
            }
        except:
            project['github_info'] = { 'Info' : 'Github Repository Not Found'}
    else:
        project['github_info'] = { 'Info' : 'Github Repository Not Found'}
    
    
    return render_template('projectdetails.html', project=project)





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
        attribute_inuse = request.form.get("inuse", False)
        
        if attribute_inuse == "on":
            attribute_inuse = True
        else:
            attribute_inuse = False
        
        connected_collection = request.form["ConnectedCollection"]
        
        if attribute_type == 'Array':
            array_contents = request.form.getlist('array_contents[]')
            db.configurations.insert_one({
                'name': attribute_name, 
                'type': attribute_type, 
                'inuse': attribute_inuse, 
                'ArrayContents': array_contents, 
                'ConnectedCollection': connected_collection
            })
        else:
            db.configurations.insert_one({
                'name': attribute_name, 
                'type': attribute_type, 
                'inuse': attribute_inuse, 
                'ConnectedCollection': connected_collection
            })
        
        return redirect(url_for('configuration'))
    else:
        collection_names = db.list_collection_names()
        collection_names = [name for name in collection_names if name != 'configurations']
        
        return render_template('makeconfig.html', bson_types=bson_types, collections=collection_names)


@app.route('/config_inuse/<string:id>', methods=['POST'])
def config_inuse(id):
    config = db.configurations.find_one({'_id': ObjectId(id)})
    if config:
        inuse = config.get('inuse', math.nan)
        # Check if inuse is NaN or False, set to True, else set to False
        if inuse != inuse or not inuse:  # Check for NaN or False
            db.configurations.update_one({'_id': ObjectId(id)}, {'$set': {'inuse': True}})
        else:
            db.configurations.update_one({'_id': ObjectId(id)}, {'$set': {'inuse': False}})
    return redirect(url_for('configuration'))



@app.route('/editconfig/<string:id>', methods=['GET', 'POST'])
def editconfig(id):
    configuration = db.configurations.find_one({'_id': ObjectId(id)})
    if request.method == 'POST':
        attribute_name = request.form['attributename']
        attribute_type = request.form['attributetype']
        attribute_inuse = request.form.get("inuse", False)
        if attribute_inuse == "on":
            attribute_inuse = True
        else:
            attribute_inuse = False
        
        connected_collection = request.form["ConnectedCollection"]
        
        update_data = {
            'name': attribute_name,
            'type': attribute_type,
            'inuse': attribute_inuse,
            'ConnectedCollection': connected_collection
        }
        
        if attribute_type == 'Array':
            array_contents = request.form.getlist('array_contents[]')
            update_data['ArrayContents'] = array_contents
        

        db.configurations.update_one({'_id': ObjectId(id)}, {'$set': update_data})
        return redirect(url_for('configuration'))
    else:
        collection_names = db.list_collection_names()
        collection_names = [name for name in collection_names if name != 'configurations']
        
        return render_template('editconfig.html', bson_types=bson_types, configuration=configuration, collections=collection_names)





@app.route('/onderzoekers')
def onderzoekers():
    onderzoekers_data = db.onderzoekers.find()
    
    df = pd.DataFrame(list(onderzoekers_data))
    
    table_columns = df.columns.tolist()
    
    table_rows = df.to_dict(orient='records')

    return render_template('onderzoekers.html', table_columns=table_columns, table_rows=table_rows)


@app.route('/create_onderzoeker', methods=['GET', 'POST'])
def create_onderzoeker():
    configurations = db.configurations.find({'inuse': True, 'ConnectedCollection': 'onderzoekers'})  # Fetch configurations where inuse=True
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        
        # Validate email address
        if not is_valid_email(email):
            return render_template('error.html', error_message='Invalid email address.')
        
        # Process dynamic fields
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
                dynamic_fields[attribute_name] = request.form[attribute_name]
            elif attribute_type == 'Binary Data':
                dynamic_fields[attribute_name] = request.files[attribute_name].read()
            elif attribute_type == 'Undefined':
                dynamic_fields[attribute_name] = None
            elif attribute_type == 'Null':
                dynamic_fields[attribute_name] = None

        # Save onderzoeker to the database
        db.onderzoekers.insert_one({'name': name, 'email': email, **dynamic_fields})
        
        return redirect(url_for('onderzoekers'))
    else:
        return render_template('createonderzoeker.html', configurations=configurations)

    

@app.route('/edit_onderzoeker/<string:id>', methods=['GET', 'POST'])
def edit_onderzoeker(id):
    configurations = db.configurations.find({'inuse': True, 'ConnectedCollection': 'onderzoekers'})  # Fetch configurations where inuse=True
    onderzoeker = db.onderzoekers.find_one({'_id': ObjectId(id)})
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        
        # Validate email address
        if not is_valid_email(email):
            return render_template('error.html', error_message='Invalid email address.')
        
        # Process dynamic fields
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
                dynamic_fields[attribute_name] = request.form[attribute_name]
            elif attribute_type == 'Binary Data':
                dynamic_fields[attribute_name] = request.files[attribute_name].read()
            elif attribute_type == 'Undefined':
                dynamic_fields[attribute_name] = None
            elif attribute_type == 'Null':
                dynamic_fields[attribute_name] = None

        # Update onderzoeker in the database
        db.onderzoekers.update_one(
            {'_id': ObjectId(id)},
            {'$set': {'name': name, 'email': email, **dynamic_fields}}
        )
        
        return redirect(url_for('onderzoekers'))
    else:
        return render_template('editonderzoeker.html', configurations=configurations, onderzoeker=onderzoeker)

    

@app.route('/overkoepelende_projects')
def overkoepelende_projects():
    projects = db.overkoepelende_projects.find()
    
    df = pd.DataFrame(list(projects))
    
    table_columns = df.columns.tolist()
    
    table_rows = df.to_dict(orient='records')

    return render_template('overprojects.html', table_columns=table_columns, table_rows=table_rows)


@app.route('/create_overkoepelende_project', methods=['GET', 'POST'])
def create_overkoepelende_project():
    configurations = db.configurations.find({'inuse': True, 'ConnectedCollection': 'overkoepelende_projects'})  # Fetch configurations where inuse=True
    if request.method == 'POST':
        research_project = request.form['research_project']

        # Check for duplicate research_project
        if db.overkoepelende_projects.find_one({'research_project': research_project}):
            flash(f"The research project '{research_project}' already exists.", 'error') # type: ignore
            return render_template('createover.html', configurations=configurations)

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
                dynamic_fields[attribute_name] = request.form[attribute_name]
            elif attribute_type == 'Binary Data':
                dynamic_fields[attribute_name] = request.files[attribute_name].read()
            elif attribute_type == 'Undefined':
                dynamic_fields[attribute_name] = None
            elif attribute_type == 'Null':
                dynamic_fields[attribute_name] = None

        researchprojectcode = format_overproject_number(get_next_overproject_code())

        db.overkoepelende_projects.insert_one({'research_project': research_project,'research_project_code' : researchprojectcode,**dynamic_fields})
        return redirect(url_for('overkoepelende_projects'))
    else:
        return render_template('createover.html', configurations=configurations)

@app.route('/edit_overkoepelende_project/<string:id>', methods=['GET', 'POST'])
def edit_overkoepelende_project(id):
    project = db.overkoepelende_projects.find_one({'_id': ObjectId(id)})
    print(project)
    configurations = db.configurations.find({'inuse': True, 'ConnectedCollection': 'overkoepelende_projects'})
    
    if request.method == 'POST':
        research_project = request.form['research_project']
        
        # Check for duplicate research_project
        existing_project = db.overkoepelende_projects.find_one({'research_project': research_project})
        if existing_project and str(existing_project['_id']) != id:
            flash(f"The research project '{research_project}' already exists.", 'error') # type: ignore
            return render_template('editover.html', project=project, configurations=configurations)

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
                dynamic_fields[attribute_name] = request.form[attribute_name]
            elif attribute_type == 'Binary Data':
                dynamic_fields[attribute_name] = request.files[attribute_name].read()
            elif attribute_type == 'Undefined':
                dynamic_fields[attribute_name] = None
            elif attribute_type == 'Null':
                dynamic_fields[attribute_name] = None

        dynamic_fields['research_project'] = research_project
        db.overkoepelende_projects.update_one({'_id': ObjectId(id)}, {'$set': dynamic_fields})
        return redirect(url_for('overkoepelende_projects'))
    else:
        return render_template('editover.html', project=project, configurations=configurations)





@app.route('/owe')
def owe():
    owe_data = db.owe.find() 
    
    df = pd.DataFrame(list(owe_data))
    
    table_columns = df.columns.tolist()
    
    table_rows = df.to_dict(orient='records')

    return render_template('owe.html', table_columns=table_columns, table_rows=table_rows)




@app.route('/create_owe', methods=['GET', 'POST'])
def create_owe():
    configurations = db.configurations.find({'inuse': True, 'ConnectedCollection': 'owe'})  # Fetch configurations where inuse=True and ConnectedCollection is 'owe'
    if request.method == 'POST':
        name = request.form['name']
        
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
                dynamic_fields[attribute_name] = request.form[attribute_name]
            elif attribute_type == 'Binary Data':
                dynamic_fields[attribute_name] = request.files[attribute_name].read()
            elif attribute_type == 'Undefined':
                dynamic_fields[attribute_name] = None
            elif attribute_type == 'Null':
                dynamic_fields[attribute_name] = None
        
        db.owe.insert_one({'name': name, **dynamic_fields})

        return redirect(url_for('owe'))
    else:
        return render_template('createowe.html', configurations=configurations)




@app.route('/edit_owe/<string:id>', methods=['GET', 'POST'])
def edit_owe(id):
    owe = db.owe.find_one({'_id': ObjectId(id)})
    configurations = db.configurations.find({'inuse': True, 'ConnectedCollection': 'owe'})

    if request.method == 'POST':
        name = request.form['name']
        
        # Check for duplicate name
        existing_owe = db.owe.find_one({'name': name})
        if existing_owe and str(existing_owe['_id']) != id:
            flash(f"The OWE with name '{name}' already exists.", 'error') # type: ignore
            return render_template('editowe.html', owe=owe, configurations=configurations)
        
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
                dynamic_fields[attribute_name] = request.form[attribute_name]
            elif attribute_type == 'Binary Data':
                dynamic_fields[attribute_name] = request.files[attribute_name].read()
            elif attribute_type == 'Undefined':
                dynamic_fields[attribute_name] = None
            elif attribute_type == 'Null':
                dynamic_fields[attribute_name] = None

        dynamic_fields['name'] = name
        db.owe.update_one({'_id': ObjectId(id)}, {'$set': dynamic_fields})
        return redirect(url_for('owe'))  # Change to your actual OWE list route
    else:
        return render_template('editowe.html', owe=owe, configurations=configurations)






@app.route('/githubrepos')
def github_repos():
    gh = GhApi()

    token = os.environ.get('GH_TOKEN2')

    gh = GhApi(token=token)

    org = os.environ.get('GH_ORG')

    repos = gh.repos.list_for_org(org)

    return render_template('githubrepos.html', repos=repos)



@app.route('/delete_repo/<path:repo_url>', methods=['POST'])
def delete_repo(repo_url):
    parsed_url = urlparse(repo_url)
    path_parts = parsed_url.path.split('/')
    owner = path_parts[1]
    repo_name = path_parts[2]

    token = os.environ.get('GH_TOKEN2')
    gh = GhApi(token=token)

    try:
        gh.repos.delete(owner=owner, repo=repo_name)
    except Exception as e:
        return f"Failed to delete repository from GitHub: {str(e)}", 500

    return redirect(url_for('github_repos'))



@app.route('/downloads')
def downloads():
    return render_template('downloads.html')

@app.route('/downloadexcel')
def downloadexcel():
    projects = list(db.projects.find())
    overkoepelende_projects = list(db.overkoepelende_projects.find())
    configurations = list(db.configurations.find())
    onderzoekers = list(db.onderzoekers.find())
    owe_data = list(db.owe.find())

    gh = GhApi()
    token = os.environ.get('GH_TOKEN2')
    gh = GhApi(token=token)
    org = os.environ.get('GH_ORG')
    repos = gh.repos.list_for_org(org)

    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer) as writer:
        pd.DataFrame(projects).to_excel(writer, sheet_name='Projects', index=False)
        pd.DataFrame(overkoepelende_projects).to_excel(writer, sheet_name='Overkoepelende Projects', index=False)
        pd.DataFrame(configurations).to_excel(writer, sheet_name='Configurations', index=False)
        pd.DataFrame(onderzoekers).to_excel(writer, sheet_name='Onderzoekers', index=False)
        pd.DataFrame(owe_data).to_excel(writer, sheet_name='Owe Data', index=False)
        pd.DataFrame(repos).to_excel(writer, sheet_name='GithubRepos', index=False)

    excel_buffer.seek(0)
    return send_file(excel_buffer, as_attachment=True, attachment_filename='mongo_data.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@app.route('/download_csv_zip')
def download_csv_zip():
    projects = pd.DataFrame(list(db.projects.find()))
    overkoepelende_projects = pd.DataFrame(list(db.overkoepelende_projects.find()))
    configurations = pd.DataFrame(list(db.configurations.find()))
    onderzoekers = pd.DataFrame(list(db.onderzoekers.find()))
    owe_data = pd.DataFrame(list(db.owe.find()))

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        projects_csv = projects.to_csv(index=False, encoding='utf-8-sig')
        zip_file.writestr('projects.csv', projects_csv)
        
        overkoepelende_projects_csv = overkoepelende_projects.to_csv(index=False, encoding='utf-8-sig')
        zip_file.writestr('overkoepelende_projects.csv', overkoepelende_projects_csv)
        
        configurations_csv = configurations.to_csv(index=False, encoding='utf-8-sig')
        zip_file.writestr('configurations.csv', configurations_csv)
        
        onderzoekers_csv = onderzoekers.to_csv(index=False, encoding='utf-8-sig')
        zip_file.writestr('onderzoekers.csv', onderzoekers_csv)
        
        owe_data_csv = owe_data.to_csv(index=False, encoding='utf-8-sig')
        zip_file.writestr('owe_data.csv', owe_data_csv)

    zip_buffer.seek(0)
    return send_file(zip_buffer, as_attachment=True, attachment_filename='mongo_data.zip', mimetype='application/zip')


@app.route('/download_json')
def download_json():
    projects = list(db.projects.find())

    for project in projects:
        if 'project_image' in project and project['project_image']:
            project['project_image'] = str(project['_id']) + '.webp'
    
        if 'overkoepelende_project' in project:
            overkoepelende_project = db.overkoepelende_projects.find_one({'_id': ObjectId(project['overkoepelende_project'])})
            overkoepelende_project.pop('_id', None)
            project['overkoepelende_project'] = overkoepelende_project

        if 'onderzoeker' in project:
            onderzoeker = db.onderzoekers.find_one({'_id': ObjectId(project['onderzoeker'])})
            onderzoeker.pop('_id', None)
            project['onderzoeker'] = onderzoeker

        if 'owe' in project:
            owe_obj = db.owe.find_one({'_id': ObjectId(project['owe'])})
            owe_obj.pop('_id', None)
            project['owe'] = owe_obj
        
        if 'githubrepo' in project:
            token = os.environ.get('GH_TOKEN2')
            gh = GhApi(token=token)
            
            github_url = project['githubrepo']
            owner, repo_name = github_url.split('/')[-2:]

            repo = gh.repos.get(owner=owner, repo=repo_name)

            contributors = gh.repos.list_contributors(owner=owner, repo=repo_name)
            contributors_list = [contributor.login for contributor in contributors]

            project['github_info'] = {
                'name': repo.name,
                'description': repo.description,
                'owner': repo.owner.login,
                'visibility': 'Private' if repo.private else 'Public',
                'language': repo.language,
                'contributors': contributors_list,
                'topics': ', '.join(repo.topics)
            }
        
        project.pop('_id', None)

    
    return jsonify(projects)