from flask_wtf import FlaskForm
from wtforms.fields import (
    StringField,
    SubmitField,
    HiddenField,
    SelectMultipleField,
    SelectField
)
from wtforms.validators import (
    InputRequired,
    Length,
)

from flask import (
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    jsonify
)
from app import metadata
from app.utils import Operations

class FocusSampleForm(FlaskForm):
    samples = SelectField(label="Focus", render_kw={'class':'search clearable'})


class NewClusterForm(FlaskForm):
    species = SelectField(label='Species', choices=[(x,x) for x in metadata.clusterSpecies], validators=[InputRequired()], render_kw={'class':'search'})
    sts = SelectField(label='ST', choices=[], validators=[InputRequired()], render_kw={'class':'search'})
    name = StringField('Name', validators=[InputRequired(), Length(1, 64)])
    members = SelectMultipleField(label='Members', choices=[], validators=[InputRequired()], render_kw={'class':'search'})
    submit = SubmitField('Create')

    def validate(self):
        rv = FlaskForm.validate(self)

        if not rv:
            return False

        if len(self.members.data) < 2:
            self.members.errors.append('Cluster requires two or more samples')
            return False

        if metadata.existingClusterName(self.name.data):
            self.name.errors.append("Name already taken")
            return False

        if not metadata.validateSpecies(self.species.data):
            self.species.errors.append("Bad species")
            return False

        if not metadata.validateST(self.species.data, self.sts.data):
            self.sts.errors.append("Bad ST")
            return False

        if not metadata.validateCluster(self.species.data, self.sts.data, self.members.data):
            self.members.append("Bad members")
            return False

        return True 


class EditClusterForm(NewClusterForm):
    originalname = HiddenField('oname', validators=[InputRequired()])
    species = StringField(label='Species', validators=[InputRequired()], render_kw={'class':'disabled'})
    sts = StringField(label='ST', validators=[InputRequired()], render_kw={'class':'disabled'})
    members = NewClusterForm.members
    submit = SubmitField('Update')

    def validate(self):
        rv = FlaskForm.validate(self)

        if not rv:
            return False

        if len(self.members.data) < 2:
            self.members.errors.append('Cluster requires two or more samples')
            return False

        print(f"OG: {self.originalname.data}")
        print(f"Name: {self.name.data}")
        print(f"Members: {self.members.data}")

        if self.name.data != self.originalname.data:
            if metadata.existingClusterName(self.name.data):
                self.name.errors.append("Name already taken")
                return False

        if not metadata.validateSpecies(self.species.data):
            self.species.errors.append("Bad species")
            return False

        if not metadata.validateST(self.species.data, self.sts.data):
            self.sts.errors.append("Bad ST")
            return False

        if not metadata.validateCluster(self.species.data, self.sts.data, self.members.data):
            self.members.append("Bad members")
            return False

        return True 


def manage_clusters():
    """View all clusters."""
    return render_template(
        'admin/manage_clusters.html', clusters=metadata.clusters)


def cluster_info(cluster_id):
    """View a cluster."""
    cluster = metadata.getICluster(cluster_id)
    if cluster is None:
        abort(404)
    return render_template('admin/manage_cluster.html', cluster=cluster, cluster_id=cluster_id)


def edit_cluster(cluster_id):
    """Edit cluster."""
    cluster = metadata.getICluster(cluster_id)
    if cluster is None:
        abort(404)
    species = cluster['SPECIES']
    st = cluster['ST']
    form = EditClusterForm()
    samples = metadata.getSTSMembers(species, st, asDict=False)
    form.members.choices = [(x,x) for x in samples['Sample ID']]
    focus = FocusSampleForm()
    focus.samples.choices = [("","")]+[(x,x) for x in metadata.getSTSMembers(species, st)['Sample ID']]
    if request.method == 'GET':
        form.originalname.data = cluster['CLUSTER']
        form.species.data = species
        form.sts.data = st
        form.name.data = cluster['CLUSTER']
        form.members.data = [x for x in cluster['MEMBERS'].split(';')]
        focus.samples.data = []
    distances = metadata.getDistances(species, st)
    
    if form.validate_on_submit():
        cluster = metadata.getICluster(cluster_id, asDict=False)
        clusters = metadata.clusters
        clusters.iloc[cluster.name]["SPECIES"] = form.species.data
        clusters.iloc[cluster.name]["ST"] = form.sts.data
        clusters.iloc[cluster.name]["CLUSTER"] = form.name.data
        clusters.iloc[cluster.name]["MEMBERS"] = ';'.join(form.members.data)
        metadata.clusters = clusters
        cluster = metadata.getICluster(cluster_id)
        Operations.restart_shiny()
        flash('Successfully updated cluster {}.'.format(form.name.data), 'form-success')
    return render_template('admin/manage_cluster.html', cluster=cluster, form=form, focus=focus, samples=samples, distances=distances, cluster_id=cluster_id)


def delete_cluster_request(cluster_id):
    """Request deletion of a cluster"""
    cluster = metadata.getICluster(cluster_id, asDict=False)
    if cluster is None:
        abort(404)
    return render_template('admin/manage_cluster.html', cluster=cluster, cluster_id=cluster_id)


def delete_cluster(cluster_id):
    """Delete a cluster."""
    cluster = metadata.getICluster(cluster_id, asDict=False)
    if cluster is None:
        abort(404)
    clusters = metadata.clusters
    clusters = clusters.drop(cluster.name)
    metadata.clusters = clusters
    Operations.restart_shiny()
    flash('Successfully deleted cluster %s.' % cluster['CLUSTER'], 'success')
    return redirect(url_for('admin.manage_clusters'))


def new_cluster():
    """Create a new cluster."""
    defaultSpecies = 'Escherichia coli'
    defaultST = '131'
    form = NewClusterForm()
    focus = FocusSampleForm()
    if request.method == 'GET':
        form.species.data = defaultSpecies
        form.sts.data = defaultST

    form.sts.choices = [(x, x) for x in metadata.getSpeciesSTs(form.species.data, clusterable=True)]
    form.members.choices = [(x, x) for x in metadata.getSTSMembers(form.species.data, form.sts.data)['Sample ID']]
    focus.samples.choices = [("","")]+[(x,x) for x in metadata.getSTSMembers(form.species.data, form.sts.data)['Sample ID']]
    focus.samples.data = []
    samples = metadata.getSTSMembers(form.species.data, form.sts.data, asDict=False)
    distances = metadata.getDistances(form.species.data, form.sts.data)

    if form.validate_on_submit():
        cluster = {}
        cluster['SPECIES'] = form.species.data
        cluster['ST'] = form.sts.data
        cluster['CLUSTER'] = form.name.data
        cluster['MEMBERS'] = ';'.join(form.members.data)
        clusters = metadata.clusters
        clusters = clusters.append(cluster, ignore_index=True)
        metadata.clusters = clusters
        Operations.restart_shiny()
        flash('Cluster {} successfully created'.format(form.name.data),
              'form-success')
    return render_template('admin/new_cluster.html', form=form, focus=focus, samples=samples, distances=distances)


def get_sts():
    """Route to populate STs for a given species."""
    species = request.args.get('species')
    sts = metadata.getSpeciesSTs(species, clusterable=True)
    return jsonify({'sts': sts})


def get_members():
    """Route to populate members for given a species and ST"""
    species = request.args.get('species')
    ST = request.args.get('st')
    members = metadata.getSTSMembers(species, ST)
    return jsonify({'members': members})

def get_distances():
    """Route to get distance matrix for given a species and ST"""
    species = request.args.get('species')
    ST = request.args.get('st')
    distances = metadata.getDistances(species, ST)
    return jsonify({'distances': distances})


def get_metadata():
    """Route to get metadata for given a species and ST"""
    species = request.args.get('species')
    ST = request.args.get('st')
    samples = metadata.getSTSMembers(species, ST, asDict=False)
    samples = list(samples.T.to_dict().values())
    return jsonify({'metadata': samples})