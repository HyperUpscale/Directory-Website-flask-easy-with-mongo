from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from bson.objectid import ObjectId
from jinja2 import Environment, pass_context

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/directory"
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
mongo = PyMongo(app)
app.jinja_env.filters['makeset'] = lambda seq: set(seq)

# Home route
@app.route('/')
def index():
    categories = mongo.db.categories.find()
    parameters = mongo.db.parameters.find()

    search_query = request.args.get('search', '')
    if search_query:
        resources = mongo.db.resources.find({
            '$or': [
                {'title': {'$regex': search_query, '$options': 'i'}},
                {'description': {'$regex': search_query, '$options': 'i'}},
                {'category': {'$regex': search_query, '$options': 'i'}},
                {'parameters': {'$regex': search_query, '$options': 'i'}}
            ]
        })
    else:
        resources = mongo.db.resources.find()

    return render_template('index.html', categories=categories, resources=resources, parameters=parameters)

# Category route
@app.route('/category/<category_id>')
def category(category_id):
    category = mongo.db.categories.find_one({'_id': ObjectId(category_id)})
    resources = mongo.db.resources.find({'category': category_id})
    parameters = mongo.db.parameters.find()
    return render_template('category.html', category=category, resources=resources, parameters=parameters)

# Add category route
@app.route('/add_category', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        category_name = request.form['category_name']
        mongo.db.categories.insert_one({'name': category_name})
        return redirect(url_for('index'))
    return render_template('add_category.html')

@app.route('/categories', methods=['GET', 'POST'])
def categories():
    if request.method == 'POST':
        category_name = request.form['category_name']
        mongo.db.categories.insert_one({'name': category_name})
        return redirect(url_for('index'))
    categories = mongo.db.categories.find()
    return render_template('categories.html', categories=categories)

# Define a route for the delete_category endpoint
@app.route('/delete_category/<category_id>', methods=['POST'])
def delete_category(category_id):
    # Add code to handle deletion of category here
    return "Category deleted successfully"  # Placeholder response
# Update category route
@app.route('/update_category/<category_id>', methods=['GET', 'POST'])
def update_category(category_id):
    category = mongo.db.categories.find_one({'_id': ObjectId(category_id)})
    if request.method == 'POST':
        new_name = request.form['new_name']
        mongo.db.categories.update_one({'_id': ObjectId(category_id)}, {'$set': {'name': new_name}})
        return redirect(url_for('index'))
    return render_template('update_category.html', category=category)

# Add resource route
@app.route('/add', methods=['GET', 'POST'])
def add_resource():
    categories = mongo.db.categories.find()
    parameters = mongo.db.parameters.find()
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        else:
            filename = None

        resource_parameters = request.form.getlist('parameters') or []

        resource = {
            'title': request.form['title'],
            'description': request.form['description'],
            'category': request.form['category'],
            'link': request.form['link'],
            'filename': filename,
            'parameters': resource_parameters,
            'created_at': datetime.utcnow()
        }
        mongo.db.resources.insert_one(resource)
        return redirect(url_for('index'))
    return render_template('add_resource.html', categories=categories, parameters=parameters)

# Update resource route
@app.route('/update_resource/<resource_id>', methods=['GET', 'POST'])
def update_resource(resource_id):
    resource = mongo.db.resources.find_one({'_id': ObjectId(resource_id)})
    categories = mongo.db.categories.find()
    parameters = mongo.db.parameters.find()
    if request.method == 'POST':
        # Handle form data and update the resource
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)
        else:
            file_path = resource['file_path']

        resource_parameters = request.form.getlist('parameters')

        updated_resource = {
            'title': request.form['title'],
            'description': request.form['description'],
            'category': request.form['category'],
            'link': request.form['link'],
            'file_path': file_path,
            'parameters': resource_parameters,
            'created_at': resource['created_at']
        }
        mongo.db.resources.update_one({'_id': ObjectId(resource_id)}, {'$set': updated_resource})
        return redirect(url_for('index'))
    return render_template('update_resource.html', resource=resource, categories=categories, parameters=parameters)

# Add parameter route
@app.route('/add_parameter', methods=['POST'])
def add_parameter():
    parameter_name = request.form['parameter_name']
    mongo.db.parameters.insert_one({'name': parameter_name})
    return redirect(url_for('index'))

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000, debug=True)