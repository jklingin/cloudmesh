from datetime import datetime
from flask import Blueprint
from flask import Flask, render_template, request, redirect
from cloudmesh.config.cm_keys import cm_keys

from cloudmesh.config.cm_projects import cm_projects
from cloudmesh.config.cm_config import cm_config

profile_module = Blueprint('profile_module', __name__)

#
# ROUTE: PROFILE
#


@profile_module.route('/profile/', methods=['GET', 'POST'])
def profile():
    # bug the global var of the ditc should be used

    config = cm_config()
    configuration = config.get()
    projects = cm_projects()
    person = configuration['profile']
    keys = cm_keys()
    version = "tmp"

    if request.method == 'POST':
        print request.form
        print "p", projects
        # print "c", config
        projects.default = request.form['field-selected-project']
        configuration['security']['default'] = request.form[
            'field-selected-securityGroup']
        config.index = request.form['field-index']
        config.prefix = request.form['field-prefix']
        config.firstname = request.form['field-firstname']
        config.lastname = request.form['field-lastname']
        config.phone = request.form['field-phone']
        config.email = request.form['field-email']

        print "setting the values"
        config.default_cloud = request.form['field-default-cloud']
        # print request.form["field-cloud-activated-" + value]
        print "setting the cloud values"
        # print config
        config.write()
        print "WRITING DONE"

    time_now = datetime.now().strftime("%Y-%m-%d %H:%M")

    address = '<br>'.join(str(x) for x in person['address'])
    return render_template('profile.html',
                           updated=time_now,
                           keys=keys,
                           projects=projects,
                           person=person,
                           address=address,
                           # clouds=clouds,
                           config=config,
                           configuration=configuration,
                           version=version,
                           )
