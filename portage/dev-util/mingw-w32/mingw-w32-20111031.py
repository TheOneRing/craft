# -*- coding: utf-8 -*-
import utils
import shutil
import os
import info

class subinfo(info.infoclass):
    def setTargets( self ):
        ver = "20111031"
        self.targets[ver] = "http://downloads.sourceforge.net/sourceforge/kde-windows/mingw/mingw-w32-bin_i686-mingw_20111031_sezero_aheinecke.tar.gz"
        self.targetDigests["20111031"] = '52973249d5ee43be94bc785f9340d1c9c1fbfc3b'
        self.defaultTarget = ver
        
        ver = "4.7.0"
        self.targets[ver] = "http://downloads.sourceforge.net/sourceforge/mingw-w64/i686-w64-mingw32-gcc-4.7.0-release-win32_rubenvb.7z"
        self.targetDigests['4.7.0'] = '5d97139ea6b4634581375ebc3fecc81c56df8686'
        self.patchToApply['4.7.0'] = ("unknw.diff", 0)

    def setDependencies( self ):
        self.buildDependencies['virtual/bin-base'] = 'default'

from Package.BinaryPackageBase import *

class Package(BinaryPackageBase):
    def __init__( self):
        self.subinfo = subinfo()
        self.subinfo.options.merge.ignoreBuildType = True
        BinaryPackageBase.__init__(self)

    def install(self):
        shutil.move( os.path.join( self.installDir() , "mingw32" ) , os.path.join( self.installDir(), "mingw" ) )
        if self.subinfo.buildTarget == "20111031":
            shutil.copy( os.path.join( self.installDir() , "mingw" , "bin" , "gmake.exe") , os.path.join( self.installDir() , "mingw" , "bin" , "mingw32-make.exe") )
            utils.applyPatch( self.imageDir(), os.path.join( self.packageDir(), "gcc_Exit.diff"), 0 )
        return True

if __name__ == '__main__':
    Package().execute()
