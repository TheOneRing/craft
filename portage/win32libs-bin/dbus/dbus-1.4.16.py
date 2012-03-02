# This package-script is automatically updated by the script win32libsupdater.py
# which can be found in your emerge/bin folder. To update this package, run
# win32libsupdater.py (and commit the results)
# based on revision git300e71be83450407a947422dca7250fbfcbbea49

from Package.BinaryPackageBase import *
import os
import info

class subinfo( info.infoclass ):
    def setTargets( self ):
        repoUrl = 'http://downloads.sourceforge.net/kde-windows'

        for version in [ '1.4.0', '1.4.1', '1.2.4-1', '1.4.0-1', '1.4.1-1', '1.4.1-2', '1.4.10', '1.4.16' ]:
            self.targets[ version ]          = self.getPackage( repoUrl, 'dbus', version )
            self.targetDigestUrls[ version ] = self.getPackage( repoUrl, 'dbus', version, '.tar.bz2.sha1' )

        self.shortDescription = '''Freedesktop message bus system (daemon and clients)'''

        self.defaultTarget = '1.4.16'


    def setDependencies( self ):
        if not utils.envAsBool( 'EMERGE_ENABLE_IMPLICID_BUILDTIME_DEPENDENCIES' ):
            self.buildDependencies[ 'virtual/bin-base' ] = 'default'
        self.runtimeDependencies[ 'win32libs-bin/expat' ] = 'default'


    def setBuildOptions( self ):
        self.disableHostBuild = False
        self.disableTargetBuild = True

class Package(BinaryPackageBase):
  def __init__(self):
    self.subinfo = subinfo()
    BinaryPackageBase.__init__( self )

if __name__ == '__main__':
    Package().execute()
