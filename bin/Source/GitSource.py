# -*- coding: utf-8 -*-
# git support

from VersionSystemSourceBase import *
import os
import utils
from shells import *

# todo requires installed git package -> add suport for installing packages 

class GitSource (VersionSystemSourceBase):
    """git support"""
    def __init__(self):
        VersionSystemSourceBase.__init__(self)        
        self.shell = MSysShell()

    def fetch( self, repopath=None, packagedir=None ):
        if repopath == None:
            repopath = self.repositoryPath()

        if packagedir == None:
            packagedir = self.packagedir
            
        ret = True
        if ( not self.noFetch ):
            safePath = os.environ["PATH"]
            os.environ["PATH"] = os.path.join(self.rootdir, "git", "bin") + ";" + safePath
            if os.path.exists( self.sourceDir() ):
                """if directory already exists, simply do a pull but obey to offline"""
                ret = self.shell.execute( self.sourceDir(), "git", "pull" )
            else:
                """it doesn't exist so clone the repo"""
                # todo we need to enter into one level above the source directory 
                ret = self.shell.execute( self.sourceDir().replace(self.package,""), "git", "clone %s %s" % ( repopath, self.package ) )
            os.environ["PATH"] = safePath
        else:
            utils.debug( "skipping git fetch (--offline)" )
        return ret
