from conans import CMake, ConanFile, tools
import os

class BraftConan(ConanFile):
    name = "braft"
    version = "1.1.2"
    license = "https://github.com/baidu/braft/blob/master/LICENSE"
    url = "https://github.com/jjkoshy/conan-recipes/conan-braft"
    description = "An industrial-grade C++ implementation of RAFT consensus algorithm based on brpc"
    settings = "os", "compiler", "build_type", "arch", "arch_build"
    options = {
            "shared": [True, False],
            "with_snappy": [True, False] }
    default_options = {
            "shared": False,
            "with_snappy": False }
    generators = ('cmake_paths', 'CMakeDeps')
    requires = (
        'brpc/1.3.0@ambroff/testing',
        'crc32c/1.1.2',
        'gflags/2.2.2',
        'leveldb/1.23',
    )
    exports_sources = ('patches/*',)

    def config(self):
        self.options['glog'].shared = False
        self.options['gflags'].shared = False
        self.options['gflags'].nothreads = False
        self.options['leveldb'].with_snappy = self.options.with_snappy

    @property
    def zip_folder_name(self):
        return "%s-%s" % (self.name, self.version)

    def source(self):
        zip_name = "%s.zip" % self.version
        tools.download("https://github.com/baidu/braft/archive/v%s.zip" % self.version, zip_name)
        tools.unzip(zip_name)
        tools.check_md5(zip_name, "0f6453db19b5708007190c0cd5471348")
        os.unlink(zip_name)
        with tools.chdir(self.zip_folder_name):
            #tools.patch(patch_file='../patches/braft-%s.patch' % self.version, strip=1)
            os.system('patch -p1 < ../patches/braft-%s.patch' % self.version)

    def configure_cmake(self):
        cmake = CMake(self)
        # uncomment for non-parallel builds
        # cmake.parallel = False
        # cmake_paths generator produces conan_paths.cmake
        cmake.definitions["CMAKE_TOOLCHAIN_FILE"] = "conan_paths.cmake"
        cmake.configure(
            source_folder = 'braft-%s' % self.version,
            defs={
                'CMAKE_POSITION_INDEPENDENT_CODE': True,
                'BRAFT_REVISION': 'a90cf6071',
            })
        return cmake

    def build(self):
        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", "braft-%s" % self.version, keep_path=False)
        cmake = self.configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["braft"]
