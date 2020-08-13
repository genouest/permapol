from flask import render_template, jsonify, redirect, request, render_template_string
from app import app
from functools import wraps
from .forms import CreateGroupForm


def check_remote_login(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        # Do the check here, or redirect if fail:
        # Check if the header is set, and that the user actually exists
        # Might need to cache the request?
        return func(*args, **kwargs)
    return decorated_function

@app.route('/')
@app.route('/index')
@check_remote_login
def index():
    groups = _get_user_groups("mateo.boudet@gmail.com")
    organisms = _get_user_organisms("mateo.boudet@gmail.com")
    return render_template('home.html', title='Home', admin_groups=groups['admin'], user_groups=groups['user'], organisms=organisms)

@app.route('/groups/create', methods=['GET', 'POST'])
@check_remote_login
def create_group():
    form = CreateGroupForm()
    if form.validate_on_submit():
        pass
    elif request.method == 'GET':
        return render_template_string('_partial_group_create.html', form=form)
    else:
        data = json.dumps(form.errors, ensure_ascii=False)
        return jsonify(data)

def _get_user_organisms(username):
    wa = app.config["APOLLO_INSTANCE"]
    # Will organism the user has direct access to, not organism with access through groups
    # This should avoid loss of control over the organism visibility
    organisms = wa.users.get_organism_permissions(username)
    organism_list = [organism['organism'] for organism in organisms if "WRITE" in organism['permissions']]
    return organism_list

def _get_user_groups(username):
    wa = app.config["APOLLO_INSTANCE"]
    groups = wa.users.show_user(username)['groups']
    user_groups = {"admin": [], "user": []}
    for group in groups:
        gp = wa.groups.get_group_admin(group['name'])
        if username in [admin['username'] for admin in gp]:
            user_groups["admin"].append(group['name'])
            admins = ", ".join([admin['username'] for admin in gp if not admin['username'] == app.config['APOLLO_USER']])
            user_groups["user"].append({'admins': admins, 'name': group['name']})
        else:
            # Ignore groups where the admin is only the apollo admin (ldap groups...)
#            admins = ", ".join([admin['username'] for admin in gp if not admin['username'] == app.config['APOLLO_USER']])
            admins = ", ".join([admin['username'] for admin in gp])
            if admins:
                user_groups["user"].append({'admins': admins, 'name': group['name']})
    return user_groups

def _create_group(group_name, user_name):
    wa = app.config["APOLLO_INSTANCE"]
    group = wa.groups.create_group(group_name)
    group_id = group['id']
    wa.groups.update_group_admin(group_id, [user_name])
    wa.users.add_to_group(group_name, user_name)

def _add_user_to_group(group_name, user_name):
    wa = app.config["APOLLO_INSTANCE"]
    wa.users.add_to_group(group_name, user_name)


