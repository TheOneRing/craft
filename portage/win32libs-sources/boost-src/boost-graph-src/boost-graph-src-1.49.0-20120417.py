import info
class subinfo(info.infoclass):
    def setTargets(self):
        for ver in ['1.44.0', '1.47.0', '1.48.0', '1.49.0']:
            self.targets[ver] = ''
            self.targetInstSrc[ver] = 'graph'.replace('-','_')
        self.defaultTarget = '1.49.0'
        self.shortDescription = 'portable C++ libraries'


    def setDependencies( self ):
        self.buildDependencies['virtual/base'] = 'default'
        self.dependencies['win32libs-bin/boost-headers'] = 'default'
        self.dependencies['win32libs-bin/boost-regex'] = 'default'
        self.dependencies['win32libs-bin/boost-bjam'] = 'default'


from Package.BoostPackageBase import *

class Package( BoostPackageBase ):
    def __init__(self, **args):
        self.subinfo = subinfo()
        BoostPackageBase.__init__(self)


if __name__ == '__main__':
    Package().execute()
