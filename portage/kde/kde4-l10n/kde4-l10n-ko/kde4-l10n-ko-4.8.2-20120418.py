import os
import info

class subinfo( info.infoclass ):
    def setTargets( self ):
        for ver in ['4.8.1', '4.8.2']:
          self.targets[ ver] = 'ftp://ftp.kde.org/pub/kde/stable/%s/src/kde-l10n/kde-l10n-ko-%s.tar.xz' % (ver , ver )
          self.targetInstSrc[ ver] = 'kde-l10n-ko-%s'  % ver

        self.defaultTarget = '4.8.2'


    def setDependencies( self ):
        self.buildDependencies['dev-util/cmake'] = 'default'
        self.buildDependencies['enterprise5/kdelibs-e5'] = 'default'
        self.buildDependencies['dev-util/gettext-tools'] = 'default'


from Package.CMakePackageBase import *

class Package( CMakePackageBase ):
    def __init__( self ):
        self.subinfo = subinfo()
        CMakePackageBase.__init__( self )


if __name__ == '__main__':
    Package().execute()
