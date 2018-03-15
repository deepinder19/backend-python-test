from alayatodo import app
from flask import (
    redirect,
    render_template,
    request,
    session,
    jsonify
    )
from models import User, Todos, db
from utilities import login_required


@app.route('/')
def home():
    with app.open_resource('../README.md', mode='r') as f:
        readme = "".join(l.decode('utf-8') for l in f)
        return render_template('index.html', readme=readme)


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_POST():
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        # password not added to session variable
        session['user'] = {'username': user.username, 'id': user.id}
        session['logged_in'] = True
        return redirect('/todo')
    return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    return redirect('/')


@app.route('/todo/<id>', methods=['GET'])
@login_required
def todo(id):
    todo = Todos.query.filter_by(id=id, user_id=session['user']['id']).first_or_404()
    return render_template('todo.html', todo=todo)


@app.route('/todo/<id>/json', methods=['GET'])
@login_required
def todo_json(id):
    todo = Todos.query.filter_by(id=id, user_id=session['user']['id']).first_or_404()
    return jsonify(id=todo.id,
                user_id=todo.user_id,
                description=todo.description)


@app.route('/todo', methods=['GET'])
@app.route('/todo/', methods=['GET'])
@login_required
def todos():
    todos = Todos.query.filter_by(user_id=session['user']['id'])
    return render_template('todos.html', todos=todos)


@app.route('/todo', methods=['POST'])
@app.route('/todo/', methods=['POST'])
@login_required
def todos_POST():
    desc = request.form.get('description')
    if desc:
        todo = Todos(user_id=session['user']['id'], description=desc)
        db.session.add(todo)
        db.session.commit()
    return redirect('/todo')


@app.route('/todo/<id>', methods=['POST'])
@login_required
def todo_POST(id):
    todo = Todos.query.filter_by(id=id).first()
    if request.form.get('action') == 'remove':
        db.session.delete(todo)
        db.session.commit()
    elif request.form.get('action') == 'complete':
        todo.is_complete = True
        db.session.commit()
    return redirect('/todo')
