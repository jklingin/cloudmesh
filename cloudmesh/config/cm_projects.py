from cm_config import cm_config
from string import Template
import os
import json
import sys


class cm_projects:

    def _path_expand(self, text):
        """ returns a string with expanded variavble """
        template = Template(text)
        result = template.substitute(os.environ)
        result = os.path.expanduser(result)
        return result

    def __init__(self, filename=None):
        """initializes based on cm_config and returns pointer to the projects dict."""
        # Check if the file exists
        if filename is None:
            self.config = cm_config()
        else:
            self.filename = self._path_expand(filename)
            try:
                with open(self.filename):
                    pass
            except IOError:
                print 'ERROR: cm_projects, file "%s" does not exist' % self.filename
                sys.exit()
            self.config = cm_config(self.filename)

    @property
    def default(self):
        """returns the default project"""
        return self.config.data['cloudmesh']['projects']['default']

    @default.setter
    def default(self, name):
        """sets the default project"""
        # check if name is in active projects
        # if it is, set the new default project.
        # if it is not through an exception and spit out a nice msg
        # explaining that the default project needs to be set
        self.config.data['cloudmesh']['projects']['default'] = name

    def add(self, name, status="active"):
        """adds a project with given status"""
        # add the name to the following array (make sure it is an array ;-)
        if status != 'default':
            self.config.data['cloudmesh']['projects'][status].append(name)

    def delete(self, name):
        """adds a project with given status"""
        # add the name to the following array (make sure it is an array ;-)
        self.config.data['cloudmesh']['projects']['active'].remove(name)

    def names(self, status="active"):
        """returns all projects in an array with a specified status"""
        return self.config.data['cloudmesh']['projects'][status]

    def __str__(self):
        """returns the dict in a string representing the project"""
        # untested
        text = self.config.data['cloudmesh']['projects']
        return str(text)

    def dump(self):
        """returns the dict in a string representing the project"""
        # untested
        return json.dumps(self.config.data['cloudmesh']['projects'], indent=4)

    def write(self):
        """writes the updated dict to the config"""
        self.config.write()
