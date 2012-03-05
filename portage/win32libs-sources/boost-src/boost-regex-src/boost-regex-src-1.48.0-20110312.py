import os
import shutil

import utils

import info
import compiler

class subinfo(info.infoclass):
    def setTargets(self):      
        version = portage.getPackageInstance('win32libs-bin', 'boost-headers').subinfo.defaultTarget
        self.targets[version] = ''
        self.targetInstSrc[version] = "regex"
        
        self.defaultTarget = version
        self.shortDescription = "portable C++ libraries"

    def setDependencies(self):
        self.buildDependencies['win32libs-bin/boost-headers'] = 'default'
        self.buildDependencies['win32libs-bin/boost-bjam'] = 'default'
        
from Package.BoostPackageBase import *

class Package(BoostPackageBase):
    def __init__(self, **args):
        self.subinfo = subinfo()
        BoostPackageBase.__init__(self)

if __name__ == '__main__':
    Package().execute()
