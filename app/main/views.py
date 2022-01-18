from flask import Blueprint, render_template
from app import app
import app.cluster as cluster

main = Blueprint('main', __name__)
clust = Blueprint('admin', __name__)

if app.config['STAND_ALONE'] == False:
    from app.models import EditableHTML
    @main.route('/')
    def index():
        # editable_html_obj = EditableHTML.get_editable_html('home')
        # return render_template('main/index.html', editable_html_obj=editable_html_obj)
        return render_template('main/index.html')


    @main.route('/about')
    def about():
        # editable_html_obj = EditableHTML.get_editable_html('about')
        # return render_template('main/about.html', editable_html_obj=editable_html_obj)
        return render_template('main/about.html')

else:
    @main.route('/')
    def index():
        return render_template('main/index.html', editable_html_obj="", standalone=True)


    @main.route('/about')
    def about():
        return render_template('main/about.html', editable_html_obj="")


    @clust.route('/clusters')
    def manage_clusters():
        return cluster.manage_clusters()


    @clust.route('/cluster/<cluster_id>')
    @clust.route('/cluster/<cluster_id>/info')
    def cluster_info(cluster_id):
        return cluster.cluster_info(cluster_id)


    @clust.route('/cluster/<cluster_id>/edit', methods=['GET', 'POST'])
    def edit_cluster(cluster_id):
        return cluster.edit_cluster(cluster_id)


    @clust.route('/cluster/<cluster_id>/delete')
    def delete_cluster_request(cluster_id):
        return cluster.delete_cluster_request(cluster_id)


    @clust.route('/cluster/<cluster_id>/_delete')
    def delete_cluster(cluster_id):
        return cluster.delete_cluster(cluster_id)


    @clust.route('/new-cluster', methods=['GET', 'POST'])
    def new_cluster():
        return cluster.new_cluster()


    @clust.route('/get_sts')
    def get_sts():
        return cluster.get_sts()


    @clust.route('/get_members')
    def get_members():
        return cluster.get_members()

    @clust.route('/get_distances')
    def get_distances():
        return cluster.get_distances()


    @clust.route('/get_metadata')
    def get_metadata():
        return cluster.get_metadata()
