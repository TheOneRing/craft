import info

class subinfo(info.infoclass):
    def setTargets( self ):
        self.svnTargets['gitHEAD'] = ''
        self.defaultTarget = 'gitHEAD'

    def setDependencies( self ):
        self.dependencies['kde/gwenview'] = 'default'
        self.dependencies['kde/kamera'] = 'default'
        self.dependencies['kde/kcolorchooser'] = 'default'
        self.dependencies['kde/kdegraphics-strigi-analyzer'] = 'default'
        self.dependencies['kde/kdegraphics-thumbnailers'] = 'default'
        self.dependencies['kde/kolourpaint'] = 'default'
        self.dependencies['kde/kruler'] = 'default'
        self.dependencies['kde/ksaneplugin'] = 'default'
        self.dependencies['kde/ksnapshot'] = 'default'
        self.dependencies['kde/libkdcraw'] = 'default'
        self.dependencies['kde/libkexiv2'] = 'default'
        self.dependencies['kde/libkipi'] = 'default'
        self.dependencies['kde/libksane'] = 'default'
        self.dependencies['kde/kdegraphics-mobipocket'] = 'default'
        self.dependencies['kde/okular'] = 'default'
        self.dependencies['kde/svgpart'] = 'default'

from Package.VirtualPackageBase import *

class Package( VirtualPackageBase ):
    def __init__( self ):
        self.subinfo = subinfo()
        VirtualPackageBase.__init__( self )


if __name__ == '__main__':
    Package().execute()
