""" run with

nosetests -v --nocapture

or

nosetests -v

"""
import sys
sys.path.insert(0, '..')

from cloudmesh.config.cm_config import cm_config

import json
import os
import warnings
import pprint
pp = pprint.PrettyPrinter(indent=4)

from cloudmesh.util.util import HEADING


class Test_cloudmesh:

    # filename = "credentials-example.yaml"
    filename = None

    def setup(self):
        print "READING THE FILE", self.filename
        if self.filename is None:
            self.config = cm_config()
        else:
            self.config = cm_config(self.filename)

    def tearDown(self):
        pass

    def test01_print(self):
        print self.config

    def test02_active(self):
        HEADING("LIST ACTIVE PROJECTS")
        result = self.config.projects('active')
        print result
        assert 'fg82' in result

    def test03_completed(self):
        HEADING("LIST COMPLETED PROJECTS")
        result = self.config.projects('completed')
        assert True

    def test04_active(self):
        HEADING("LIST ACTIVE PROJECTS")
        result = self.config.projects('default')
        assert result == 'fg82'

    def test05_india(self):
        HEADING("LIST India")
        result = self.config.get('india-openstack-essex')
        assert result["OS_VERSION"] == "essex"

    def test06_keys_india_openstack(self):
        HEADING("KEY india-openstack")
        keys = self.config.keys()
        assert 'india-openstack-essex' in keys

    """
    def test07_keys_india_eucalyptus(self):
        HEADING("KEY india-eucalyptus")
        keys = self.config.keys()
        assert 'india-eucalyptus' in keys

    def test09_keys_india_eucalyptus(self):
        HEADING("KEY azure")
        keys = self.config.keys()
        assert 'azure' in key

    """

    def test08_keys_grizzly_openstack(self):
        HEADING("KEY sierra-openstack-grizzly")
        keys = self.config.keys()
        assert 'sierra-openstack-grizzly' in keys

    def test10_grizzly(self):
        HEADING("LIST GRIZZLY")
        result = self.config.get('sierra-openstack-grizzly')
        assert result["OS_VERSION"] == 'grizzly'

    def test11_grizzly(self):
        HEADING("LIST GRIZZLY EXPANDED")
        result = self.config.get('sierra-openstack-grizzly', expand=True)
        assert result["OS_VERSION"] == 'grizzly'

    def test12_clouds(self):
        HEADING("CLOUD")
        clouds = self.config.clouds()
        assert isinstance(clouds, dict)
        assert 'india-openstack-essex' in clouds

    def test13_cloud(self):
        HEADING("CLOUD")
        india_cloud = self.config.cloud('india-openstack-essex')
        assert isinstance(india_cloud, dict)
        assert 'cm_host' in india_cloud
        assert india_cloud['cm_host'] == 'india.futuregrid.org'

    def test14_cloud_default(self):
        HEADING("CLOUD")
        assert self.config.cloud_default(
            'india-openstack-essex', 'flavor') == 'm1.tiny'
        assert self.config.cloud_default(
            'india-openstack-essex', 'not defined') is None

    def test15_project_default(self):
        HEADING("PROJECT")
        project = self.config.projects('default')
        assert project == 'fg82'

    def test16_write(self):
        HEADING("WRITE")
        warnings.filterwarnings(
            'ignore', 'tempnam', RuntimeWarning)  # we open the file securely
        name = os.tempnam()
        print self.config
        self.config.write(name)
        print open(name, "rb").read()
        os.remove(name)

    def test17_key(self):
        HEADING("KEY")
        keys = self.config.userkeys()

        # print "DEFAULT>", self.config.userkeys('default')
        # print "TEST>", self.config.userkeys('test')

        print keys, keys['default'], keys['keylist'][keys['default']]
        assert ('default' in keys) and (keys['default'] in keys['keylist'])

    def test20_set_index_and_prefix(self):
        print
        print "INDEX:", self.config.index
        print "PREFIX:", self.config.prefix

        self.config.prefix = "hallo"
        self.config.index = "3"

        print "INDEX:", self.config.index
        print "PREFIX:", self.config.prefix
        print "NAME:", self.config.vmname

        self.config.incr()

        print "INDEX:", self.config.index
        print "PREFIX:", self.config.prefix
        print "NAME:", self.config.vmname

        assert self.config.index == 4 and self.config.prefix == "hallo"

    def test21_default(self):
        HEADING("TEST 21 DEFAULT ")
        self.config.default = "hallo"
        print self.config.default
        assert self.config.default == "hallo"

    def test22_filter(self):
        HEADING("TEST 22 FILTER")
        print self.config.get_filter('sierra-openstack-grizzly')
