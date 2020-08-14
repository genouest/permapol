from flask import render_template, jsonify, redirect, request, session, url_for
from app import app
from functools import wraps
from .forms import CreateGroupForm
import json

def check_remote_login(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        # Do the check here, or redirect if fail:
        # Check if the header is set, and that the user actually exists
        # Might need to cache the request?
        wa = app.config["APOLLO_INSTANCE"]
        username = "mateo.boudet@gmail.com"
        # Check cookie
        if not 'username' in session:
            if wa.users.show_user(username):
                session['username'] = "mateo.boudet@gmail.com"
            else:
                pass
                # Redirect?
        return func(*args, **kwargs)
    return decorated_function

@app.route('/')
@app.route('/index')
@check_remote_login
def index():
    groups = _get_user_groups(session['username'])
    organisms = _get_user_organisms(session['username'])
    return render_template('home.html', title='Home', admin_groups=groups['admin'], user_groups=groups['user'], organisms=organisms)

@app.route('/groups/view/<id>', methods=['GET', 'POST'])
@check_remote_login
def view_group(id):
    group = _get_group(id)
    if not group:
        return redirect(url_for('index'))
    if not session['username'] in [admin['email'] for admin in group['admin']]:
        return redirect(url_for('index'))
    user_organisms = _get_user_organisms(session['username'])
    set_organisms = [orga['organism'] for orga in group['organismPermissions']]
    available_organisms = [organism for organism in user_organisms if organism['name'] not in set_organisms]
    return render_template('group.html', group=group, available_organisms=available_organisms, current_user=session['username'])

@app.route('/groups/create', methods=['GET', 'POST'])
@check_remote_login
def create_group():
    form = CreateGroupForm()
    if form.validate_on_submit():
        group_id = _create_group(form.group_name.data, session['username'])
        return jsonify(status='ok', redirect=url_for('index', id=group_id))
    elif request.method == 'GET':
        return render_template('_partial_group_create.html', form=form)
    else:
        data = json.dumps(form.errors, ensure_ascii=False)
        return jsonify(data)

def _get_group(group_id):
    # Apollo does not handle errors gracefully, so cleanup the data
    wa = app.config["APOLLO_INSTANCE"]
    group = None
    try:
        group_id = int(group_id)
    except ValueError:
        return group
    try:
        group = wa.groups.show_group(group_id)
    except Exception:
        pass
    return group

def _get_user_organisms(username):
    wa = app.config["APOLLO_INSTANCE"]
    # Will organism the user has direct access to, not organism with access through groups
    # This should avoid loss of control over the organism visibility
    organisms = wa.users.get_organism_permissions(username)
    organism_list = [{"name": organism['organism'], "id": organism['id']} for organism in organisms if "WRITE" in organism['permissions']]
    return organism_list

def _get_user_groups(username):
    wa = app.config["APOLLO_INSTANCE"]
    groups = wa.users.show_user(username)['groups']
    user_groups = {"admin": [], "user": []}
    for group in groups:
        gp = wa.groups.get_group_admin(group['name'])
        if username in [admin['username'] for admin in gp]:
            # Really inefficient way to get the id. Id should be returned in the show_user call...
            id = wa.groups.get_groups(group['name'])[0]['id']
            user_groups["admin"].append({'name': group['name'], 'id':id})
            admins = ", ".join([admin['username'] for admin in gp if not admin['username'] == app.config['APOLLO_USER']])
            user_groups["user"].append({'admins': admins, 'name': group['name']})
        else:
            # Ignore groups where the admin is only the apollo admin (ldap groups...)
            admins = ", ".join([admin['username'] for admin in gp if not admin['username'] == app.config['APOLLO_USER']])
            if admins:
                user_groups["user"].append({'admins': admins, 'name': group['name']})
    return user_groups

def _create_group(group_name, user_name):
    wa = app.config["APOLLO_INSTANCE"]
    group = wa.groups.create_group(group_name)
    group_id = group['id']
    wa.groups.update_group_admin(group_id, [user_name])
    wa.users.add_to_group(group_name, user_name)
    return group_id

def _add_user_to_group(group_name, user_name):
    wa = app.config["APOLLO_INSTANCE"]
    wa.users.add_to_group(group_name, user_name)


