import info

class subinfo( info.infoclass ):
    def setTargets( self ):
        self.svnTargets['gitHEAD'] = "[git]kde:calligra"
        self.defaultTarget = 'gitHEAD'
        self.shortDescription = "The Calligra Suite of Applications"

    def setDependencies( self ):
        self.buildDependencies['kdesupport/eigen2'] = 'default'
        self.buildDependencies['win32libs-sources/glew-src'] = 'default'
        self.dependencies['win32libs-bin/lcms2'] = 'default'
        self.dependencies['virtual/kde-runtime'] = 'default'
        self.dependencies['virtual/kdepimlibs'] = 'default'
        self.dependencies['kdesupport/poppler'] = 'default'
        self.dependencies['kdesupport/qca'] = 'default'
        self.dependencies['testing/gsl'] = 'default'
        self.dependencies['win32libs-bin/exiv2'] = 'default'
        self.dependencies['win32libs-bin/openjpeg'] = 'default'
#        self.dependencies['win32libs-bin/libfftw'] = 'default'

from Package.CMakePackageBase import *

class Package( CMakePackageBase ):
    def __init__( self ):
        self.subinfo = subinfo()
        CMakePackageBase.__init__( self )
        defines = ""
        defines += "-DBUILD_kexi=OFF "
        defines += "-DBUILD_plan=OFF "
        defines += "-DBUILD_doc=OFF "
        defines += "-DMEMORY_LEAK_TRACKER=OFF"

        self.subinfo.options.configure.defines = defines

if __name__ == '__main__':
    Package().execute()
