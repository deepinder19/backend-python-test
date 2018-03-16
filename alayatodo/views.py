"""
This module defines the view of the app. All the endpoint routes are
defined in this module.
"""

from alayatodo import app
from flask import (
    redirect,
    render_template,
    request,
    session,
    jsonify,
    flash
    )
from models import User, Todos, db
from utilities import login_required

PER_PAGE = 5
HTTP_NOT_FOUND = 404


@app.route('/')
def home():
    """
    Function to get information on the landing page.
    """
    with app.open_resource('../README.md', mode='r') as f:
        readme = "".join(l.decode('utf-8') for l in f)
        return render_template('index.html', readme=readme)


@app.route('/login', methods=['GET'])
def login():
    """
    This function takes user to the login page.
    """
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_POST():
    """
    This function implements login for the user
    """
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        # Security issue: password removed from session variable
        session['user'] = {'username': user.username, 'id': user.id}
        session['logged_in'] = True
        return redirect('/todo/')
    flash('Incorrect username or password', 'error')
    return redirect('/login')


@app.route('/logout')
def logout():
    """
    This function provides logout to the user
    """
    session.pop('logged_in', None)
    session.pop('user', None)
    return redirect('/')


@app.route('/todo/<id>/', methods=['GET'])
@login_required
def todo(id):
    """
    Get all details of a todo by id

    Attributes
    ----------
    id : int
        Unique id of a todo
    """
    todo = Todos.query.filter_by(id=id, user_id=session['user']['id']).first_or_404()
    return render_template('todo.html', todo=todo)


@app.route('/todo/<id>/json', methods=['GET'])
@login_required
def todo_json(id):
    """
    Get JSON format details of a todo by id
    
    Attributes
    ----------
    id : int
        Unique id of a todo
    """
    todo = Todos.query.filter_by(id=id, user_id=session['user']['id']).first()
    if todo:
        return jsonify(id=todo.id,
                user_id=todo.user_id,
                description=todo.description)
    else:
        return jsonify({'msg': 'Could not find todo with given ID.'}), HTTP_NOT_FOUND


@app.route('/todo/', defaults={'page_num': 1}, methods=['GET'])
@app.route('/todo/page/<int:page_num>', methods=['GET'])
@login_required
def todos(page_num):
    """
    Get list of all todos for the user in paginated form
    
    Attributes
    ----------
    pagenum : int
        Page number for paginated data
    """
    todos = Todos.query.filter_by(user_id=session['user']['id']).paginate( \
                        per_page=PER_PAGE, page=page_num, error_out=True)
    return render_template('todos.html', todos=todos)


@app.route('/todo/', methods=['POST'])
@login_required
def todos_POST():
    """
    Function to add a new todo to the list
    """
    desc = request.form.get('description')
    if desc:
        todo = Todos(user_id=session['user']['id'], description=desc)
        db.session.add(todo)
        db.session.commit()
        flash('Todo added successfully!')
    else:
        flash('Description can not be empty!', 'error')
    return redirect('/todo')


@app.route('/todo/<id>', methods=['POST'])
@login_required
def todo_POST(id):
    """
    Function to update, delete a todo from the list
    
    Attributes
    ----------
    id : int
        Unique id of a todo
    """
    todo = Todos.query.filter_by(id=id).first()
    if request.form.get('action') == 'remove':
        db.session.delete(todo)
        db.session.commit()
        flash('Todo deleted successfully!')
    elif request.form.get('action') == 'complete':
        todo.is_complete = True
        db.session.commit()
        flash('Todo marked as Completed!')
    return redirect('/todo')
