from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    send_file
)
from flask_login import current_user, login_required, fresh_login_required

from app import app, db

from app.admin.forms import (
    InviteUserForm,
    NewUserForm,
    EditUserForm,
    NewGroupForm,
    EditGroupForm
)
from app.decorators import admin_required
from app.email import send_email
from app.models import EditableHTML, Role, User, Group
from app.utils import Operations
import app.cluster as cluster

admin = Blueprint('admin', __name__)


@admin.route('/')
@login_required
@admin_required
def index():
    """Admin dashboard page."""
    return render_template('admin/index.html')


@admin.route('/restart-shiny')
@login_required
@admin_required
def restart_shiny():
    """Trigger shiny server restart"""
    Operations.restart_shiny()
    flash("Shiny R Server restart triggered", "info")
    return render_template('admin/index.html')


# @admin.route('/restart-cathai')
# @login_required
# @admin_required
# def restart_cathai():
#     """Trigger CATHAI restart"""
#     Operations.restart_cathai()
#     flash("CATHAI restart triggered", "info")
#     return render_template('admin/index.html')

@admin.route('/export-clusters')
@login_required
@admin_required
def export_clusters():
    try:
        return send_file(f"../{app.config['DATA_DIR']}clusters.csv", as_attachment=True, attachment_filename='clusters.csv')
    except Exception as e:
        return str(e)


@fresh_login_required
@admin.route('/new-user', methods=['GET', 'POST'])
@login_required
@admin_required
def new_user():
    """Create a new user."""
    form = NewUserForm()
    if form.validate_on_submit():
        user = User(
            role=form.role.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            groups=form.groups.data,
            password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User {} successfully created'.format(user.full_name()),
              'form-success')
    return render_template('admin/new_user.html', form=form)


@fresh_login_required
@admin.route('/invite-user', methods=['GET', 'POST'])
@login_required
@admin_required
def invite_user():
    """Invites a new user to create an account and set their own password."""
    form = InviteUserForm()
    if form.validate_on_submit():
        user = User(
            role=form.role.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            groups=form.groups.data,
            email=form.email.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        invite_link = url_for(
            'account.join_from_invite',
            user_id=user.id,
            token=token,
            _external=True)
        send_email.delay(
            recipient=user.email,
            subject='You Are Invited To Join',
            template='account/email/invite',
            user=user.serial(),
            invite_link=invite_link,
        )
        form = InviteUserForm()
        print("boop")
        flash('User {} successfully invited'.format(user.full_name()),
              'form-success')        
    return render_template('admin/new_user.html', form=form)


@admin.route('/groups')
@login_required
@admin_required
def manage_groups():
    """View all user groups."""
    users = User.query.all()
    groups = Group.query.all()
    return render_template(
        'admin/manage_groups.html', users=users, groups=groups)


@admin.route('/clusters')
@login_required
@admin_required
def manage_clusters():
    return cluster.manage_clusters()


@admin.route('/cluster/<cluster_id>')
@admin.route('/cluster/<cluster_id>/info')
@login_required
@admin_required
def cluster_info(cluster_id):
    return cluster.cluster_info(cluster_id)


@fresh_login_required
@admin.route('/cluster/<cluster_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_cluster(cluster_id):
    return cluster.edit_cluster(cluster_id)


@admin.route('/cluster/<cluster_id>/delete')
@login_required
@admin_required
def delete_cluster_request(cluster_id):
    return cluster.delete_cluster_request(cluster_id)


@fresh_login_required
@admin.route('/cluster/<cluster_id>/_delete')
@login_required
@admin_required
def delete_cluster(cluster_id):
    return cluster.delete_cluster(cluster_id)


@fresh_login_required
@admin.route('/new-cluster', methods=['GET', 'POST'])
@login_required
@admin_required
def new_cluster():
    return cluster.new_cluster()


@admin.route('/get_sts')
@login_required
@admin_required
def get_sts():
    return cluster.get_sts()


@admin.route('/get_members')
@login_required
@admin_required
def get_members():
    return cluster.get_members()

@admin.route('/get_distances')
@login_required
@admin_required
def get_distances():
    return cluster.get_distances()


@admin.route('/get_metadata')
@login_required
@admin_required
def get_metadata():
    return cluster.get_metadata()


@fresh_login_required
@admin.route('/new-group', methods=['GET', 'POST'])
@login_required
@admin_required
def new_group():
    """Create a new group."""
    form = NewGroupForm()
    if form.validate_on_submit():
        group = Group(
            name=form.name.data,
            users=form.users.data
        )
        db.session.add(group)
        db.session.commit()
        flash('Group {} successfully created'.format(group.name),
              'form-success')
    return render_template('admin/new_group.html', form=form)


@admin.route('/group/<int:group_id>')
@admin.route('/group/<int:group_id>/info')
@login_required
@admin_required
def group_info(group_id):
    """View a group."""
    group = Group.query.filter_by(id=group_id).first()
    if group is None:
        abort(404)
    return render_template('admin/manage_group.html', group=group)
    

@fresh_login_required
@admin.route('/group/<int:group_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def change_group(group_id):
    """Change a group's name."""
    group = Group.query.filter_by(id=group_id).first()
    if group is None:
        abort(404)
    form = EditGroupForm(name=group.name, users=group.users)
    if form.validate_on_submit():
        group.name = form.name.data
        group.users = form.users.data
        db.session.add(group)
        db.session.commit()
        flash('Successfully updated group {}.'.format(
            group.name), 'form-success')
    return render_template('admin/manage_group.html', group=group, form=form)


@admin.route('/group/<int:group_id>/delete')
@login_required
@admin_required
def delete_group_request(group_id):
    """Request deletion of a group's account."""
    group = Group.query.filter_by(id=group_id).first()
    if group is None:
        abort(404)
    return render_template('admin/manage_group.html', group=group)


@fresh_login_required
@admin.route('/group/<int:group_id>/_delete')
@login_required
@admin_required
def delete_group(group_id):
    """Delete a group's account."""
    group = Group.query.filter_by(id=group_id).first()
    db.session.delete(group)
    db.session.commit()
    flash('Successfully deleted group %s.' % group.name, 'success')
    return redirect(url_for('admin.manage_groups'))


@admin.route('/users')
@login_required
@admin_required
def manage_users():
    """View all registered users."""
    users = User.query.all()
    roles = Role.query.all()
    return render_template(
        'admin/manage_users.html', users=users, roles=roles)


@admin.route('/user/<int:user_id>')
@admin.route('/user/<int:user_id>/info')
@login_required
@admin_required
def user_info(user_id):
    """View a user's profile."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    return render_template('admin/manage_user.html', user=user)


@fresh_login_required
@admin.route(
    '/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def change_user(user_id):
    """Edit user."""
    if current_user.id == user_id:
        flash('You cannot edit your own account from the admin dashboard. Please ask '
              'another administrator to do this.', 'error')
        return redirect(url_for('admin.user_info', user_id=user_id))

    user = User.query.get(user_id)
    if user is None:
        abort(404)
    form = EditUserForm(uid=user.id, role=user.role, first_name=user.first_name, last_name=user.last_name, email=user.email, groups=user.groups)
    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        user.groups = form.groups.data
        user.role = form.role.data
        db.session.add(user)
        db.session.commit()
        flash('User {} successfully updated.'.format(
            user.full_name()), 'form-success')
    return render_template('admin/manage_user.html', user=user, form=form)


@admin.route('/user/<int:user_id>/delete')
@login_required
@admin_required
def delete_user_request(user_id):
    """Request deletion of a user's account."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    return render_template('admin/manage_user.html', user=user)


@fresh_login_required
@admin.route('/user/<int:user_id>/_delete')
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user's account."""
    if current_user.id == user_id:
        flash('You cannot delete your own account. Please ask another '
              'administrator to do this.', 'error')
    else:
        user = User.query.filter_by(id=user_id).first()
        db.session.delete(user)
        db.session.commit()
        flash('Successfully deleted user %s.' % user.full_name(), 'success')
    return redirect(url_for('admin.manage_users'))


@fresh_login_required
@admin.route('/_update_editor_contents', methods=['POST'])
@login_required
@admin_required
def update_editor_contents():
    """Update the contents of an editor."""

    edit_data = request.form.get('edit_data')
    editor_name = request.form.get('editor_name')

    editor_contents = EditableHTML.query.filter_by(
        editor_name=editor_name).first()
    if editor_contents is None:
        editor_contents = EditableHTML(editor_name=editor_name)
    editor_contents.value = edit_data

    db.session.add(editor_contents)
    db.session.commit()
    return 'OK', 200
