import info

class subinfo( info.infoclass ):
    def setTargets( self ):
        self.svnTargets["master"] = "[git]https://github.com/KDAB/GammaRay.git"
        for ver in ["2.7.0"]:
            self.targets[ver] = "https://github.com/KDAB/GammaRay/archive/v%s.tar.gz" % ver
            self.targetInstSrc[ver] = "gammaray-%s" % ver
            self.archiveNames[ver] = "gammaray-%s.tar.gz" % ver
        self.targetDigests['2.7.0'] = (['74251d9de4bfa31994431c7a493e5de17d0b90853557a245bf3f7f4e0227fd14'], CraftHash.HashAlgorithm.SHA256)

        self.shortDescription = "GammaRay is a tool to poke around in a Qt-application and also to manipulate the application to some extent"

        self.defaultTarget = "2.7.0"

    def setDependencies( self ):
        self.dependencies['virtual/base'] = 'default'
        self.dependencies["libs/qtbase"] = "default"
        self.dependencies["frameworks/syntax-highlighting"] = "default"
        self.dependencies['qt-apps/kdstatemachineeditor'] = 'default'
        self.dependencies['win32libs/openssl'] = 'default'

from Package.CMakePackageBase import *

class Package( CMakePackageBase ):
    def __init__( self ):
        CMakePackageBase.__init__( self )
        self.subinfo.options.configure.defines = " -DGAMMARAY_MULTI_BUILD=OFF"
        self.changePackager(NullsoftInstallerPackager)


    def createPackage(self):
        self.defines["productname"] = "GammaRay"
        self.defines["website"] = "http://www.kdab.com/gammaray"
        self.defines["executable"] = "bin\\gammaray.exe"
#            self.defines["icon"] = os.path.join(os.path.dirname(__file__), "kdevelop.ico")
        if craftSettings.getboolean("QtSDK", "Enabled", False):
            self.defines["defaultinstdir"] = os.path.join(craftSettings.get("QtSDK", "Path"),
                                                          craftSettings.get("QtSDK", "Version"),
                                                          craftSettings.get("QtSDK", "Compiler"))

        self.ignoredPackages.append("binary/mysql-pkg")

        return TypePackager.createPackage(self)


