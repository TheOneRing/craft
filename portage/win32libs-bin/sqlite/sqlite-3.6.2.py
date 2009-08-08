from Package.BinaryPackageBase import *
import os
import shutil
import utils
import info

PACKAGE_NAME         = "sqlite"
PACKAGE_DLL_NAME     = "sqlite3"
PACKAGE_VER_MAJOR    = "3"
PACKAGE_VER_MINOR    = "6"
PACKAGE_VER_RELEASE  = "2"
PACKAGE_VER          = "%s.%s.%s" % ( PACKAGE_VER_MAJOR, PACKAGE_VER_MINOR, PACKAGE_VER_RELEASE )
PACKAGE_FULL_VER     = PACKAGE_VER
PACKAGE_FULL_NAME    = "%s-%s" % ( PACKAGE_NAME, PACKAGE_VER )
PACKAGE_FULL_NAME    = "%s_%s_%s" % ( PACKAGE_VER_MAJOR, PACKAGE_VER_MINOR, PACKAGE_VER_RELEASE )

SRC_URI= """
http://www.sqlite.org/sqlite-%s_%s_%s.zip
http://www.sqlite.org/sqlitedll-%s_%s_%s.zip
http://www.sqlite.org/sqlite-amalgamation-%s_%s_%s.zip
""" % ( PACKAGE_VER_MAJOR, PACKAGE_VER_MINOR, PACKAGE_VER_RELEASE, PACKAGE_VER_MAJOR, PACKAGE_VER_MINOR, PACKAGE_VER_RELEASE, PACKAGE_VER_MAJOR, PACKAGE_VER_MINOR, PACKAGE_VER_RELEASE )

class subinfo(info.infoclass):
    def setTargets( self ):
        self.targets[PACKAGE_VER] = SRC_URI
        self.defaultTarget = PACKAGE_VER

    def setDependencies( self ):
        self.hardDependencies['gnuwin32/sed'] = 'default'
    
class Package(BinaryPackageBase):
    def __init__( self, **args ):
        self.subinfo = subinfo()
        BinaryPackageBase.__init__( self )
        self.createCombinedPackage = True

    def unpack( self ):
        BinaryPackageBase.unpack( self )
        return True
        
    def install( self ):
        dst = os.path.join( self.imageDir(), "bin" )
        utils.cleanDirectory( dst )
        dst = os.path.join( self.imageDir(), "include" )
        utils.cleanDirectory( dst )
        dst = os.path.join( self.imageDir(), "lib" )
        utils.cleanDirectory( dst )

        src = os.path.join( self.imageDir(), PACKAGE_DLL_NAME + ".dll" )
        dst = os.path.join( self.imageDir(), "bin", PACKAGE_DLL_NAME + ".dll" )
        shutil.copy( src, dst )
        src = os.path.join( self.imageDir(), PACKAGE_DLL_NAME + ".exe" )
        dst = os.path.join( self.imageDir(), "bin", PACKAGE_DLL_NAME + ".exe" )
        shutil.copy( src, dst )
        src = os.path.join( self.imageDir(), PACKAGE_DLL_NAME + ".h" )
        dst = os.path.join( self.imageDir(), "include", PACKAGE_DLL_NAME + ".h" )
        shutil.copy( src, dst )
        src = os.path.join( self.imageDir(), PACKAGE_DLL_NAME + "ext.h" )
        dst = os.path.join( self.imageDir(), "include", PACKAGE_DLL_NAME + "ext.h" )
        shutil.copy( src, dst )
        src = os.path.join( self.imageDir(), PACKAGE_DLL_NAME + ".def" )
        dst = os.path.join( self.imageDir(), "lib", PACKAGE_DLL_NAME + ".def" )
        shutil.copy( src, dst )
        utils.createImportLibs( PACKAGE_DLL_NAME, self.imageDir() )
        return True

    def make_package( self ):
        self.doPackaging( PACKAGE_NAME, PACKAGE_FULL_VER, False )

        return True

if __name__ == '__main__':
    Package().execute()
