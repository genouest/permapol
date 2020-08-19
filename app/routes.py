from flask import render_template, jsonify, redirect, request, session, url_for
from app import app, cache, scheduler
from functools import wraps
from .forms import CreateGroupForm, AddUserForm
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
    # Will not show organism that the user do not have access to, even if they are associated with the group. 
    # Should not happen, but will avoid users removing groupes he does not have direct to
    added_organisms = [organism for organism in user_organisms if organism['name'] in set_organisms]
    return render_template('group.html', group=group, added_organisms=added_organisms, available_organisms=available_organisms, current_user=session['username'])

@app.route('/groups/create', methods=['GET', 'POST'])
@check_remote_login
def create_group():
    form = CreateGroupForm()
    if form.validate_on_submit():
        group_id = _create_group(form.group_name.data, session['username'])
        return jsonify(status='ok', redirect=url_for('view_group', id=group_id))
    elif request.method == 'GET':
        return render_template('_partial_group_create.html', form=form)
    else:
        data = json.dumps(form.errors, ensure_ascii=False)
        return jsonify(data)

@app.route('/groups/<group_id>/add_orga_access/<orga_id>', methods=['GET', 'POST'])
@check_remote_login
def add_orga_group(group_id, orga_id):
    group = _get_group(group_id)
    # Skip if no group or not admin
    if not group or not session['username'] in [admin['email'] for admin in group['admin']]:
        return jsonify({})
    orga = _get_organism(orga_id)
    # Skip if no organism or already has permission
    if not orga or orga['commonName'] in [organism['organism'] for organism in group['organismPermissions']]:
        return jsonify({})
    # Skip if user does not have write access to this organism (just in case)
    if not orga_id in [str(organism['id']) for organism in _get_user_organisms(session['username'])]:
        return jsonify({})

    if request.method == 'GET':
        return render_template('_partial_organism_add.html', group=group, orga=orga, action="add")
    else:
        _manage_organism(group['name'], orga['commonName'], 'add')
        return jsonify(status='ok', redirect=url_for('view_group', id=group['id']))

@app.route('/groups/<group_id>/remove_orga_access/<orga_id>', methods=['GET', 'POST'])
@check_remote_login
def remove_orga_group(group_id, orga_id):
    group = _get_group(group_id)
    # Skip if no group or not admin
    if not group or not session['username'] in [admin['email'] for admin in group['admin']]:
        return jsonify({})
    orga = _get_organism(orga_id)
    # Skip if no organism or do not have permission
    if not orga or not orga['commonName'] in [organism['organism'] for organism in group['organismPermissions']]:
        return jsonify({})

    if request.method == 'GET':
        return render_template('_partial_organism_remove.html', group=group, orga=orga, action="remove")
    else:
        _manage_organism(group['name'], orga['commonName'], 'remove')
        return jsonify(status='ok', redirect=url_for('view_group', id=group['id']))

@app.route('/groups/<group_id>/add_user', methods=['GET', 'POST'])
@check_remote_login
def add_user_group(group_id):

    group = _get_group(group_id)
    # Skip if no group or not admin
    if not group or not session['username'] in [admin['email'] for admin in group['admin']]:
        return jsonify({})

    form = AddUserForm()
    if form.validate_on_submit():
        _manage_group(group['name'], form.user_mail.data, 'add')
        return jsonify(status='ok', redirect=url_for('view_group', id=group_id))
    elif request.method == 'GET':
        if app.config.get("USER_AUTOCOMPLETE") == "TRUE":
            return render_template('_partial_user_add_autocomplete.html', form=form, group=group, user_list=_get_all_users())
        else:
            return render_template('_partial_user_add.html', form=form, group=group)
    else:
        data = json.dumps(form.errors, ensure_ascii=False)
        return jsonify(data)

@app.route('/groups/<group_id>/remove_user/<user_id>', methods=['GET', 'POST'])
@check_remote_login
def remove_user_group(group_id, user_id):
    group = _get_group(group_id)
    # Skip if no group or not admin
    if not group or not session['username'] in [admin['email'] for admin in group['admin']]:
        return jsonify({})

    user = _get_user(user_id)

    if not user or not user_id in [str(user['id']) for user in group["users"]]:
        return jsonify({})

    # Cannot remove admin
    if user['username'] in [admin['email'] for admin in group['admin']]:
        return jsonify({})

    if request.method == 'GET':
        return render_template('_partial_user_remove.html', group=group, user=user)
    else:
        _manage_group(group['name'], user['username'], 'remove')
        return jsonify(status='ok', redirect=url_for('view_group', id=group_id))

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

def _get_user(user_id):
    # Apollo does not handle errors gracefully, so cleanup the data
    wa = app.config["APOLLO_INSTANCE"]
    user = None
    try:
        user_id = int(user_id)
    except ValueError:
        return user
    try:
        user = wa.users.show_user(user_id)
    except Exception:
        pass
    return user

def _get_organism(organism_id):
    wa = app.config["APOLLO_INSTANCE"]
    orga = None
    try:
        organism_id = int(organism_id)
    except ValueError:
        return orga
    orga = wa.organisms.show_organism(organism_id)
    if "error" in orga:
        return None
    return orga

def _get_user_organisms(username):
    wa = app.config["APOLLO_INSTANCE"]
    # Will organism the user has direct access to, not organism with access through groups
    # This should avoid loss of control over the organism visibility
    organisms = wa.users.get_organism_permissions(username)
    organism_list = []
    for organism in organisms:
        if "WRITE" in organism['permissions']:
            orga = wa.organisms.show_organism(organism['organism'])
            organism_list.append({"name": orga['commonName'], "id": orga['id']})
    return organism_list

def _get_user_groups(username):
    wa = app.config["APOLLO_INSTANCE"]
    groups = wa.users.show_user(username)['groups']
    user_groups = {"admin": [], "user": []}
    for group in groups:
        gp = wa.groups.get_group_admin(group['name'])
        if username in [admin['username'] for admin in gp]:
            grp = wa.groups.get_groups(group['name'])[0]
            user_groups["admin"].append({'name': group['name'], 'id':grp['id'], "members": len(grp['users']), "organisms": len(grp['organismPermissions'])})
            admins = ", ".join([admin['username'] for admin in gp if not admin['username'] == app.config['APOLLO_USER']])
            user_groups["user"].append({'admins': admins, 'name': group['name']})
        else:
            # Ignore groups where the admin is only the apollo admin (ldap groups...)
            admins = ", ".join([admin['username'] for admin in gp if not admin['username'] == app.config['APOLLO_USER']])
            if admins:
                user_groups["user"].append({'admins': admins, 'name': group['name']})
    return user_groups

def _manage_organism(group_name, organism_name, action):
    wa = app.config["APOLLO_INSTANCE"]

    if action == "add":
        wa.groups.update_organism_permissions(group_name, organism_name, False, True, True, True)
    elif action == "remove":
        wa.groups.update_organism_permissions(group_name, organism_name)

def _manage_group(group_name, username, action):
    wa = app.config["APOLLO_INSTANCE"]
    if action == "add":
        wa.users.add_to_group(group_name, username)
    elif action == "remove":
        wa.users.remove_from_group(group_name, username)

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

def _get_all_users(refresh=False):
    val = cache.get("user_list")
    if val and not refresh:
        return val
    else:
        wa = app.config["APOLLO_INSTANCE"]
        user_list = [user['username'] for user in wa.users.get_users()]
        cache.set("user_list", user_list)
        return user_list

def _sync_permissions():
    wa = app.config["APOLLO_INSTANCE"]
    groups = wa.groups.get_groups()
    for group in groups:
        # Skip groups with admin in it
        admins = [admin['email'] for admin in group['admin']]
        if app.config["APOLLO_USER"] in admins:
            continue
        group_orga = set([orga['organism'] for orga in group['organismPermissions']])
        organisms_access = set()
        for admin in admins:
            admin_organisms = set([orga['name'] for orga in _get_user_organisms(admin)])
            organisms_access |= admin_organisms
        for missing_org in group_orga - organisms_access:
            _manage_organism(group['name'], missing_org, "remove")
            print("Organism sync : removing organism {} from group {}".format(missing_org, group['name']))
