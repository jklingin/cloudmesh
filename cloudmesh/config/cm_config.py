import sys
sys.path.insert(0, '../..')
import yaml
import os
import stat
import json
import collections

from string import Template

from cloudmesh.util.util import path_expand
from cloudmesh.util.logger import LOGGER
from cloudmesh.util.util import check_file_for_tabs
from cloudmesh.config.cloudmesh_cloud_handler import cloudmesh_cloud_handler

##### For testing
# import mock_keystone


log = LOGGER("cm_config")


class cm_config(object):

    # ----------------------------------------------------------------------
    # global variables
    # ----------------------------------------------------------------------

    default_path = '.futuregrid/cloudmesh.yaml'
    yaml_template = '%s/cloudmesh_template.yaml' % os.path.dirname(__file__)
    clouddata_template = '%s/cloudmesh_clouds.yaml' % os.path.dirname(__file__)

    filename = ""

    data = collections.OrderedDict()

    # ----------------------------------------------------------------------
    # initialization methods
    # ----------------------------------------------------------------------

    def __init__(self, filename=None):
        if filename is None:
            home = os.environ['HOME']
            self.filename = "%s/%s" % (home, self.default_path)
        else:
            self.filename = filename
        try:
            self.read(self.filename)
        except Exception, e:
            log.error(str(e))
            log.error("Can not find the file: {0}".format(self.filename))
            sys.exit()
        self._userdata_handler = None
        self._clouddata = None

        # test for tab in yaml file
        if check_file_for_tabs(self.filename):
            log.error("The file {0} contains tabs. yaml Files are not allowed to contain tabs".format(filename))
            sys.exit()
        

    @property
    def userdata_handler(self):
        """Plug-in class that knows how to get all the user/project data"""
        return self._userdata_handler

    @userdata_handler.setter
    def userdata_handler(self, value):
        self._userdata_handler = value


    @property
    def clouddata(self):
        if self._clouddata is None:
            self._clouddata = yaml.safe_load(open(self.clouddata_template, "r"))
        return self._clouddata

    # ----------------------------------------------------------------------
    # Methods to initialize (create) the config data
    # ----------------------------------------------------------------------
    def _initialize_user(self, username):
        """Loads user data, including profile, projects, and credentials"""
        user = self.userdata_handler(username)

        self.data['cloudmesh']['prefix'] = username
        self.data['cloudmesh']['index'] = "001"

        self.data['cloudmesh']['profile'] = {
            'username': username,
            'uid': user.uid,
            'gid': user.gid,
            'firstname': user.firstname,
            'lastname': user.lastname,
            'phone': user.phone,
            'e-mail': user.email,
            'address': user.address
        }

        keys = {'default': None, 'keylist': {}}
        if user.keys:
            for key in user.keys.keys():
                if keys['default'] is None:
                    keys['default'] = key
                keys['keylist'][key] = user.keys[key]
        self.data['cloudmesh']['keys'] = keys

        self.data['cloudmesh']['projects'] = {
            'active': user.activeprojects,
            'completed': user.completedprojects,
            'default': user.defaultproject
        }

        self.data['cloudmesh']['active'] = user.activeclouds
        self.data['cloudmesh']['default'] = user.defaultcloud

    def _initialize_clouds(self):
        """Creates cloud credentials for the user"""
        self.data['cloudmesh']['clouds'] = {}
        cloudlist = self.active()
        for cloud in cloudlist:
            cloudcreds_handler = cloudmesh_cloud_handler(cloud)
            cloudcreds = cloudcreds_handler(self.profile(), self.projects('default'), self.projects('active'), cloud, self.clouddata[cloud])
            ########### for testing #############################################################
            # cloudcreds._client = mock_keystone.Client
            # cloudcreds._client.mockusername = self.data['cloudmesh']['profile']['username']
            # cloudcreds._client.mocktenants = ['fg82','fg110','fg296']
            #####################################################################################
            cloudcreds.initialize_cloud_user()
            self.data['cloudmesh']['clouds'][cloud] = cloudcreds.data

    def initialize(self, username):
        """Creates or resets the data for a user.  Note that the
        userdata_handler property must be set with appropriate handler class."""
        self.data = yaml.safe_load(open(self.yaml_template, "r"))
        self._initialize_user(username)
        self._initialize_clouds()

    def change_own_password(self, oldpass, newpass):
        cloudlist = self.active()
        for cloud in cloudlist:
            cloudcreds_handler = cloudmesh_cloud_handler(cloud)
            cloudcreds = cloudcreds_handler(self.profile(), self.projects('default'), self.projects('active'), cloud, self.clouddata[cloud])
            cloudcreds.change_password(oldpass, newpass)


    # ----------------------------------------------------------------------
    # read and write methods
    # ----------------------------------------------------------------------

    def read(self, filename):
        self.filename = filename
        if os.path.exists(filename):
            f = open(self.filename, "r")
            self.data = yaml.safe_load(f)
            f.close()

    def write(self, filename=None):
        # pyaml.dump(self.data, f, vspacing=[2, 1, 1])
        # text = yaml.dump(self.data, default_flow_style=False)
        content = ""
        content = yaml.safe_dump(self.data, default_flow_style=False, indent=4)

        fpath = filename or self.filename
        f = os.open(fpath, os.O_CREAT | os.O_TRUNC |
                    os.O_WRONLY, stat.S_IRUSR | stat.S_IWUSR)
        os.write(f, content)
        os.close(f)

    # ----------------------------------------------------------------------
    # print methods
    # ----------------------------------------------------------------------
    def __str__(self):
        return json.dumps(self.data, indent=4)

    def export_line(self, attribute, value):
        if isinstance(value, (list, tuple)):
            avalue = ','.join(value)
        else:
            avalue = value
        return 'export %s="%s"\n' % (attribute, avalue)

    # ----------------------------------------------------------------------
    # get methods
    # ----------------------------------------------------------------------

    def incr(self, value=1):
        self.data['cloudmesh']['index'] = int(
            self.data['cloudmesh']['index']) + int(value)
        # self.write(self.filename)

    @property
    def vmname(self):
        return "%s-%04d" % (self.data['cloudmesh']['prefix'], int(self.data['cloudmesh']['index']))

    #
    # warning we can not name a method default
    #
    @property
    def default_cloud(self):
        return self.data['cloudmesh']['default']

    @default_cloud.setter
    def default_cloud(self, value):
        self.data['cloudmesh']['default'] = str(value)

    def active(self):
        return self.data['cloudmesh']['active']

    @property
    def prefix(self):
        return self.data['cloudmesh']['prefix']

    @prefix.setter
    def prefix(self, value):
        self.data['cloudmesh']['prefix'] = value

    @property
    def index(self):
        return self.data['cloudmesh']['index']

    @index.setter
    def index(self, value):
        self.data['cloudmesh']['index'] = int(value)

    @property
    def firstname(self):
        return self.data['cloudmesh']['profile']['firstname']

    @firstname.setter
    def firstname(self, value):
        self.data['cloudmesh']['profile']['firstname'] = str(value)

    @property
    def lastname(self):
        return self.data['cloudmesh']['profile']['lastname']

    @lastname.setter
    def lastname(self, value):
        self.data['cloudmesh']['profile']['lastname'] = str(value)

    @property
    def phone(self):
        return self.data['cloudmesh']['profile']['phone']

    @phone.setter
    def phone(self, value):
        self.data['cloudmesh']['profile']['phone'] = str(value)

    @property
    def email(self):
        return self.data['cloudmesh']['profile']['e-mail']

    @email.setter
    def email(self, value):
        self.data['cloudmesh']['profile']['e-mail'] = str(value)

    @property
    def address(self):
        return self.data['cloudmesh']['profile']['address']

    @address.setter
    def address(self, value):
        self.data['cloudmesh']['profile']['address'] = str(value)

    def profile(self):
        return self.data['cloudmesh']['profile']

    def userkeys(self, attribute=None, expand=True):
        if attribute is None:
            return self.data['cloudmesh']['keys']
        else:
            if attribute == 'default':
                name = self.data['cloudmesh']['keys']['default']
                value = self.data['cloudmesh']['keys']['keylist'][name]
            else:
                value = self.data['cloudmesh']['keys']['keylist'][attribute]
            if expand:
                value = path_expand(value)
            return value

    def default(self, cloudname):
        return self.data['cloudmesh']['clouds'][cloudname]['default']

    def projects(self, status):
        return self.data['cloudmesh']['projects'][status]

    def clouds(self):
        return self.data['cloudmesh']['clouds']

    def cloud(self, cloudname):
        return self.data['cloudmesh']['clouds'][cloudname] if cloudname in self.data['cloudmesh']['clouds'] else None

    def cloud_default(self, cloudname, defname):
        cloud = self.cloud(cloudname)
        defaults = cloud['default'] if 'default' in cloud else []
        return defaults[defname] if defname in defaults else None

    def get(self, key=None, expand=False):
        if key is None:
            return self.data['cloudmesh']
        else:
            if expand:
                d = self.cloud(key)['credentials']
                for key in d:
                    d[key] = path_expand(d[key])
                return d
            else:
                return self.cloud(key)['credentials']

    # This method may not be exactly what I think it is, but based on usage it
    # appears as if it is supposed to get the keys of the clouds

    def keys(self):
        return self.clouds().keys()

    def rc(self, name):
        result = self.get(name)
        lines = ""
        for (attribute, value) in iter(sorted(result.iteritems())):
            lines += self.export_line(attribute, value)
        return lines

    def rc_euca(self, name, project):
        result = self.cloud(name)
        eucakeydir = 'EUCA_KEY_DIR'
        lines = self.export_line(eucakeydir, result[eucakeydir])

        for (attribute, value) in result.iteritems():
            if attribute != eucakeydir:
                if type(value) is dict:
                    if attribute == project:
                        for (pattribute, pvalue) in value.iteritems():
                            lines += self.export_line(pattribute, pvalue)
                else:
                    lines += self.export_line(attribute, value)
        return lines

    def set_filter(self, cloudname, filter, type='state'):
        # try:
        #    test = self.data['cloudmesh']['clouds'][cloudname]['default']['filter']
        # except:
        # self.data['cloudmesh']['clouds'][cloudname]['default']['filter'] = {}
        self.data['cloudmesh']['clouds'][cloudname][
            'default']['filter'][type] = filter

    def get_filter(self, cloudname, type='state'):
        print "getting the filter for cloud", cloudname
        # try:
        #    result = self.data['cloudmesh']['clouds'][cloudname]['default']['filter'][type]
        # except:
        #    self.set_filter(cloudname, {}, type)
        result = self.data['cloudmesh']['clouds'][
            cloudname]['default']['filter'][type]
        return result

    def create_filter(self, cloudname, states):
        self.data['cloudmesh']['clouds'][cloudname]['default']['filter'] = {}
        state_flags = {}
        for state in states:
            state_flags[state] = True
        self.set_filter(cloudname, state_flags, 'state')
        self.set_filter(cloudname, {'me': True}, 'select')


# ----------------------------------------------------------------------
# MAIN METHOD FOR TESTING
# ----------------------------------------------------------------------

if __name__ == "__main__":
    config = cm_config()

    print config

    print "================="
    print config.projects('active')
    print config.projects('completed')
    print "================="
    print config.get('india-openstack')
    print "================="
    print config.get()
    print "================="
    print config.keys()
    print "================="
    print config.rc('india-openstack')
    print "================="
    print config.default
    print "================="
    outfile = "%s/%s" % (os.environ['HOME'], ".futuregrid/junk.yaml")
    print config.write(outfile)
    os.system("cat " + outfile)
    print "================="
    configuration = config.get('azure')

    print configuration['username']

    print "================="

    configuration = config.get('india-eucalyptus')
    print configuration

    print configuration['host']
