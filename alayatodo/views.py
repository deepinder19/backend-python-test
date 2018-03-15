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
        return redirect('/todo/')
    return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    return redirect('/')


@app.route('/todo/<id>/', methods=['GET'])
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


@app.route('/todo/', defaults={'page_num': 1}, methods=['GET'])
@app.route('/todo/page/<int:page_num>', methods=['GET'])
@login_required
def todos(page_num):
    todos = Todos.query.filter_by(user_id=session['user']['id']).paginate(per_page=5, page=page_num, error_out=True)
    return render_template('todos.html', todos=todos)


@app.route('/todo/', methods=['POST'])
@login_required
def todos_POST():
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
