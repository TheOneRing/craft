# -*- coding: utf-8 -*-
import utils
import shutil
import os
import info

class subinfo(info.infoclass):
    def setTargets( self ):
        ver="20100702"
        self.targets[ver] = "http://downloads.sourceforge.net/sourceforge/mingw-w64/mingw-w32-bin_i686-mingw_"+ver+"_sezero.zip"
        self.defaultTarget = ver
            
    def setDependencies( self ):
        self.hardDependencies['gnuwin32/wget'] = 'default'
        self.hardDependencies['gnuwin32/patch'] = 'default'
        
from Package.BinaryPackageBase import *

class Package(BinaryPackageBase):
    def __init__( self):
        self.subinfo = subinfo()
        self.subinfo.options.merge.ignoreBuildType = True
        BinaryPackageBase.__init__(self)

    def install(self):
        shutil.move( os.path.join( self.installDir() , "mingw32" ) , os.path.join( self.installDir(), "mingw" ) )
        shutil.copy( os.path.join( self.installDir() , "mingw" , "bin" , "gmake.exe") , os.path.join( self.installDir() , "mingw" , "bin" , "mingw32-make.exe") )
        return True

if __name__ == '__main__':
    Package().execute()
