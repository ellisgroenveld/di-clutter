from flask import render_template, request, redirect, url_for
from app import app

# Sample data for projects
projects = [
    {
        "Titel": "Project 1",
        "achtergrond": "Background 1",
        "doelstelling": "Goal 1",
        "beoogd_resultaat": "Expected Result 1",
        "overkoepelend_project": "Parent Project 1",
        "onderwijs": "Education 1",
        "opmerkingen": "Comments 1"
    },
    {
        "Titel": "Project 2",
        "achtergrond": "Background 2",
        "doelstelling": "Goal 2",
        "beoogd_resultaat": "Expected Result 2",
        "overkoepelend_project": "Parent Project 2",
        "onderwijs": "Education 2",
        "opmerkingen": "Comments 2"
    }
]

@app.route('/')
def index():
    return render_template('index.html', projects=projects)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        new_project = {}
        for field in ['Titel', 'achtergrond', 'doelstelling', 'beoogd_resultaat', 'overkoepelend_project', 'onderwijs', 'opmerkingen']:
            new_project[field] = request.form[field]
        projects.append(new_project)
        return redirect(url_for('index'))
    return render_template('create.html')

@app.route('/edit/<int:index>', methods=['GET', 'POST'])
def edit(index):
    project = projects[index]
    if request.method == 'POST':
        for field in ['Titel', 'achtergrond', 'doelstelling', 'beoogd_resultaat', 'overkoepelend_project', 'onderwijs', 'opmerkingen']:
            project[field] = request.form[field]
        return redirect(url_for('index'))
    return render_template('edit.html', project=project, index=index)



@app.route('/delete/<int:index>', methods=['POST'])
def delete(index):
    del projects[index]
    return redirect(url_for('index'))

