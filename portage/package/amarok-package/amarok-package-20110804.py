# -*- coding: utf-8 -*-
import info
from Package.VirtualPackageBase import *
from Packager.NullsoftInstallerPackager import *

# This is an example package for building

class subinfo( info.infoclass ):
    def setTargets( self ):
        self.svnTargets[ '2.4.3' ] = ""
        self.defaultTarget = '2.4.3'

    def setDependencies( self ):
        self.dependencies[ 'extragear/amarok' ] = 'default'
        self.dependencies[ 'kde/kde-workspace' ] = 'default'
        self.dependencies[ 'kdesupport/snorenotify' ] = 'default'
        self.dependencies[ 'libs/runtime' ] = 'default'
        self.dependencies[ 'win32libs-bin/liblzma' ] = 'default'
        self.dependencies[ 'kdesupport/hupnp' ] = 'default'
        self.dependencies[ 'kdesupport/phonon-vlc'] = 'default'
        
class Package( NullsoftInstallerPackager, VirtualPackageBase ):
    def __init__( self, **args ):
        self.subinfo = subinfo()
        blacklists = [ NSIPackagerLists.runtimeBlacklist, 'blacklist.txt', 'blacklist-virtuoso.txt' ]
        NullsoftInstallerPackager.__init__( self, blacklists=blacklists )
        VirtualPackageBase.__init__( self )
        self.defines[ "executable" ] = "bin\\amarok.exe"
        self.defines["executable_name" ] = "Amarok"
        self.defines[ "executable2" ] = "bin\\systemsettings.exe"
        self.defines["executable2_name" ] = "Settings"
        self.defines[ "executable3" ] = "bin\\snorenotify.exe"
        self.defines["executable3_name" ] = "Snorenotify"
        self.scriptname = os.path.join(self.packageDir(),"NullsoftInstaller.nsi")

if __name__ == '__main__':
    Package().execute()
