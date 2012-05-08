---
title: Getting Charm running on Android
kind: article
created_at: 2012/05/08
tags: [python, charm, android]
featured: 0
excerpt: This is a guide to getting the Charm crypto library working on Android.
---

These are notes for getting the [Charm library](http://charm-crypto.com/Main.html) working on an Android device. 

**NB:** Move ahead to [this section](#final) if you just want to install the final APKs on a device.

Preliminaries
-------------

Start by putting everything in a new, fresh directory, named "fresh". All the instructions below will refer to that.

Working installations of git, Mercurial, Eclipse, the Android SDK, and the Android NDK are required. Setup an Android cross compilation toolchain, as below, and make sure all the required executables are inside the PATH.

<pre class="prettyprint">
export ANDROID_NDK=~/apps/android-ndk-r7c
export ANDROID_NDK_TOOLCHAIN_ROOT=~/apps/android-toolchain
$ANDROID_NDK/build/tools/make-standalone-toolchain.sh --platform=android-10 --install-dir=$ANDROID_NDK_TOOLCHAIN_ROOT
export PATH=$PATH:~/apps/android-sdk-linux/tools
export PATH=$PATH:~/apps/android-sdk-linux/platform-tools
export PATH=$PATH:~/apps/android-toolchain/bin
export PATH=$PATH:~/apps/android-ndk-r7c/toolchains/arm-linux-androideabi-4.4.3/prebuilt/linux-x86
</pre>

Compiling Python for Android (Py4A)
-----------------------------------

The first step is to get Python working on Android. The [Python for Android](https://code.google.com/p/python-for-android/) project already has most of the work done. Start off by getting the code, as below:

<pre class="prettyprint">
hg clone https://code.google.com/p/python-for-android/
</pre>

It may take a while, as the repository is large. Once that's done, build it to make sure it's working. First, however, there are some modifications that need to be done to the configuration.

In the file <code class="prettyprint">~/fresh/python-for-android/python3-alpha/python3-src/pyconfig.h</code> (right above the #endif at the bottom), add the below lines:
<pre class="prettyprint">
#define ANDROID 1  /* Useful for specific code changes. */

#define HAVE_BROKEN_MBSTOWCS 1
#undef HAVE_DEV_PTMX
#undef HAVE_GETHOSTBYNAME_R
#undef HAVE_MBRTOWC
#define HAVE_NCURSES_H 1  /* This only if you've cross compiled curses */
#undef HAVE_SETLOCALE
#undef HAVE_WCSCOLL
#undef HAVE_WCSFTIME
#undef HAVE_WCSXFRM
</pre>

The build should complete successfully, and the following .zip files should be in the output folder, <code class="prettyprint">~/fresh/python-for-android/python3-alpha/python3-src/</code>:

- python3_extras_r11.zip
- python3_r10.zip
- python3_scripts_r11.zip


Preparing Charm's Dependencies
------------------------------
Charm has a few dependencies, which must be built and prepared before Charm itself can be built.

### PyParsing

First, start off with PyParsing. Download the version required by Charm, which is 1.5.5 at the time of this writing, [from this link](http://cheeseshop.python.org/packages/source/p/pyparsing/pyparsing-1.5.5.tar.gz). Open the tarball, and from inside the folder, extract the <code class="prettyprint">pyparsing_py3.py</code> file and save it as <code class="prettyprint">~/fresh/python-for-android/python3-alpha/extra_modules/pyparsing.py</code>. (**NB:** Note the change in filename.)

### pkg_resources

As part of the egg importing process, we need to use the pkg_resources module from distribute. Download the tarball [from this link](http://pypi.python.org/packages/source/d/distribute/distribute-0.6.26.tar.gz#md5=841f4262a70107f85260362f5def8206). Open the tarball, and from inside the folder, extract the <code class="prettyprint">pkg_resources.py</code> file and save it into <code class="prettyprint">~/fresh/python-for-android/python3-alpha/extra_modules/</code>. This was written for python2, so we need to convert it to python3:

<pre class="prettyprint">
cd ~/fresh/python-for-android/python3-alpha/extra_modules
2to3 -w pkg_resources.py
rm pkg_resources.py.bak
</pre>

### OpenSSL

Charm needs to link against the Android version of openssl that's deployed on the device/emulator that's being run. The easiest way to do this for now is to just fetch the binaries and use those (assuming a connection to the device exists, using adb), as below:

<pre class="prettyprint">
cd ~/fresh/python-for-android/python3-alpha/openssl/
mkdir lib
cd lib
adb pull /system/lib/libcrypto.so .
adb pull /system/lib/libssl.so .
</pre>

### GMP

- Start off by getting GMP [here](http://ftp.gnu.org/gnu/gmp/gmp-5.0.2.tar.gz). 
- Extract the folder inside of <code class="prettyprint">~/fresh/python-for-android/python3-alpha/</code>. 
- Copy the <code class="prettyprint">xbuild.sh</code> and <code class="prettyprint">xconf.sh</code> files from <code class="prettyprint">~/fresh/python-for-android/python3-alpha/sqlite3/</code> to <code class="prettyprint">~/fresh/python-for-android/python3-alpha/gmp-5.0.2/</code>. 
- Replace the <code class="prettyprint">config.sub</code> and <code class="prettyprint">config.guess</code> files inside <code class="prettyprint">~/fresh/python-for-android/python3-alpha/gmp-5.0.2/</code> with updated versions from [here](http://git.savannah.gnu.org/gitweb/?p=config.git;a=tree).

Now, compile it:
<pre class="prettyprint">
cd ~/fresh/python-for-android/python3-alpha/gmp-5.0.2/
chmod a+x xconf.sh xbuild.sh
./xconf.sh
./xbuild.sh
</pre>

Upon a successful build, <code class="prettyprint">libgmp.so</code> should be present inside <code class="prettyprint">~/fresh/python-for-android/python3-alpha/thirdparty/lib/</code>

### PBC

Start off by getting PBC [here](http://crypto.stanford.edu/pbc/files/pbc-0.5.12.tar.gz). Extract the folder inside of <code class="prettyprint">~/fresh/python-for-android/python3-alpha/</code>. Replace the <code class="prettyprint">config.sub</code> and <code class="prettyprint">config.guess</code> files inside <code class="prettyprint">~/fresh/python-for-android/python3-alpha/pbc-0.5.12/</code> with updated versions from [here](http://git.savannah.gnu.org/gitweb/?p=config.git;a=tree).

PBC has one slight incompatibility that needs to be fixed. Replace the <code class="prettyprint">~/fresh/python-for-android/python3-alpha/pbc-0.5.12/misc/extend_printf.c</code> file with [this one](https://groups.google.com/group/pbc-devel/attach/37af39a5f6d16a73/extend_printf.c?part=4&authuser=0), as per instructions in [this thread](https://groups.google.com/forum/?fromgroups#!msg/pbc-devel/yrB2a0W3ZDc/HJTKNDI7FLAJ).

The next step is to tell PBC where to find GMP. Add two files as below. Note that the paths used are absolute paths, the ~ does not get expanded, so the full home directory must be specified.

In <code class="prettyprint">~/fresh/python-for-android/python3-alpha/pbc-0.5.12/xbuild.sh</code>:

<pre class="prettyprint">
TARGET=arm-linux-androideabi
pushd ../thirdparty
TARGET_DIR=`pwd`
popd
export CPPFLAGS='-I../gmp-5.0.2 -I../../gmp-5.0.2'
export LDFLAGS='-L/home/hasnain/fresh/python-for-android/python3-alpha/thirdparty/lib'
./configure --host=$TARGET --target=$TARGET --prefix=$TARGET_DIR && make && make install
</pre>

In <code class="prettyprint">~/fresh/python-for-android/python3-alpha/pbc-0.5.12/xconf.sh</code>:
<pre class="prettyprint">
TARGET=arm-linux-androideabi
export CPPFLAGS='-I/home/hasnain/fresh/python-for/android/python3-alpha/gmp-5.0.2'
export LDFLAGS=-L/home/hasnain/fresh/python-for-android/python3-alpha/thirdparty/lib
./configure --host=$TARGET --target=$TARGET --prefix=$PWD/compiled/$TARGET CFLAGS='-I/home/hasnain/fresh/python-for/android/python3-alpha/gmp-5.0.2'
</pre>

Now, compile it:
<pre class="prettyprint">
cd ~/fresh/python-for-android/python3-alpha/pbc-0.5.12/
chmod a+x xconf.sh xbuild.sh
./xconf.sh
./xbuild.sh
</pre>

Upon a successful build, <code class="prettyprint">libpbc.so</code> should be present inside <code class="prettyprint">~/fresh/python-for-android/python3-alpha/thirdparty/lib/</code>

### Integration with Py4A
The next step is to integrate the building of these modules with the python-for-android build. PyParsing is already handled by just placing the file inside the required directory. OpenSSL needs no work. For the others, some work is required.

Start off by making the following additions.

In <code class="prettyprint">~/fresh/python-for-android/python3-alpha/buildall.sh</code>: (above "Python 3")
<pre class="prettyprint">
echo "gmp"
pushd gmp-5.0.2
./xbuild.sh
popd
echo "pbc"
pushd pbc-0.5.12
./xbuild.sh
popd
</pre>

In <code class="prettyprint">~/fresh/python-for-android/python3-alpha/cleanall.sh</code>: (above "Python 3")
<pre class="prettyprint">
echo "gmp"
pushd gmp-5.0.2
make clean
popd
echo "pbc"
pushd pbc-0.5.12
make clean
popd
</pre>

In <code class="prettyprint">~/fresh/python-for-android/python3-alpha/python3-src/xpack.sh</code>: (above "#Symbolic linked libs just take up space")
<pre class="prettyprint">
cp ../../thirdparty/lib/libpbc.so.1.0.0 python3/lib/libpbc.so.1
cp ../../thirdparty/lib/libgmp.so.10.0.2 python3/lib/libgmp.so.10
</pre>

Do a clean build:
<pre class="prettyprint">
cd ~/fresh/python-for-android/python3-alpha
./cleanall.sh
./buildall.sh
</pre>

Verify the build by checking for the existence of <code class="prettyprint">pyparsing.py</code> and <code class="prettyprint">pkg_resources.py</code> inside <code class="prettyprint">~/fresh/python-for-android/python3-alpha/python3-src/python3_extras_r11.zip</code>; and for the existence of <code class="prettyprint">libpbc.so.1</code> and <code class="prettyprint">libgmp.so.10</code> inside <code class="prettyprint">~/fresh/python-for-android/python3-alpha/python3-src/python3_r10.zip</code>.


Building Charm
--------------

### Prerequisites

Make sure a valid installation of Python3 and setuptools is available. On Ubuntu, the following command should do it:
<pre class="prettyprint">
sudo apt-get install python3 python3-setuptools
</pre>

Fetch the Charm source:
<pre class="prettyprint">
cd ~/fresh
git clone git://github.com/mhlakhani/charm.git
</pre>


### Modifications to the Charm Source

**NOTE:** The following changes have already been done in the repository mentioned above. They are just listed here for reference.

The integermath extension in Charm uses a function which is deprecated in later versions of OpenSSL. The Ubuntu versions have that left in for backward compatibility, however it's not available on the Android version. So, the following modification is needed:

<pre class="prettyprint">
diff --git a/charm-src/integermath/integermodule.c b/charm-src/integermath/integermodule.c
index 5e77bf3..28c4a0e 100644
--- a/charm-src/integermath/integermodule.c
+++ b/charm-src/integermath/integermodule.c
@@ -1156,12 +1156,19 @@ static PyObject *genRandomPrime(Integer *self, PyObject *args) {
                        /* This routine generates safe prime only when safe=TRUE in which prime, p is selected
                         * iff (p-1)/2 is also prime.
                         */
+#ifndef ANDROID
                        if(safe == TRUE) // safe is non-zero
                                BN_generate_prime(bn, bits, safe, NULL, NULL, NULL, NULL);
                        else
                                /* generate strong primes only */
                                BN_generate_prime(bn, bits, FALSE, NULL, NULL, NULL, NULL);
-
+#else
+                       if(safe == TRUE) // safe is non-zero
+                               BN_generate_prime_ex(bn, bits, safe, NULL, NULL, NULL);
+                       else
+                               /* generate strong primes only */
+                               BN_generate_prime_ex(bn, bits, FALSE, NULL, NULL, NULL);
+#endif
                        debug("Safe prime => ");
                        print_bn_dec(bn);
                        bnToMPZ(bn, rop->e);
</pre>

Similarly, it has a workaround for the paths used in importing, which isn't really needed on Android. Modify that as well:

<pre class="prettyprint">
diff --git a/charm-src/charm/__init__.py b/charm-src/charm/__init__.py
index 1c2274a..744c0ff 100644
--- a/charm-src/charm/__init__.py
+++ b/charm-src/charm/__init__.py
@@ -3,6 +3,7 @@ import platform
 
 install_system=platform.system()
 
+path_to_charm = None
 path_to_charm2 = None
 if install_system == 'Darwin':
    # get the path to site-packages for operating system
@@ -21,7 +22,7 @@ elif install_system == 'Linux':
 else:
    print("Installing on", install_system)
    
-sys.path.append(path_to_charm + "/charm/")
+if path_to_charm: sys.path.append(path_to_charm + "/charm/")
 if path_to_charm2: sys.path.append(path_to_charm2 + "/charm/")
 # now python can easily find our modules
 # dependency for pairing, integer and ecc mods
</pre>

Lastly, we need to modify setup.py to create an egg, as that's what Py4A requires. Replace the whole of that file with the below:
<pre class="prettyprint">
from setuptools import setup, Extension
import os,platform

def patch_distutils():
    import os
    from distutils import sysconfig
    from distutils.sysconfig import get_python_inc as du_get_python_inc

    def get_python_inc(plat_specific=0, *args, **kwargs):
        if plat_specific == 0:
            out = os.environ["PY4A_INC"]
        else:
            out = du_get_python_inc(plat_specific=plat_specific, *args, **kwargs)
        return out
    setattr(sysconfig, 'get_python_inc', get_python_inc)

    def customize_compiler(compiler):
        cflags = "-I%s" % os.environ["PY4A_INC"]
        cflags+= " -I%s" % os.environ["GMP_INC"]
        cflags+= " -I%s" % os.environ["OSSL_INC"]
        cflags+= " -I."
        cflags+=" -MMD -MP -MF -fpic -ffunction-sections -funwind-tables -fstack-protector"
        cflags+=" -D__ARM_ARCH_5__ -D__ARM_ARCH_5T__ -D__ARM_ARCH_5E__ -D__ARM_ARCH_5TE__"
        cflags+=" -Wno-psabi -march=armv5te -mtune=xscale -msoft-float -mthumb -Os"
        cflags+=" -fomit-frame-pointer -fno-strict-aliasing -finline-limit=64"
        cflags+=" -DANDROID  -Wa,--noexecstack -O2 -DNDEBUG -g"
        cc = "arm-linux-androideabi-gcc"
        cxx = "arm-linux-androideabi-g++"
        cpp = "arm-linux-androideabi-cpp"
        ldshared= "%s -shared" % cxx
        ldshared+=" -L%s" % os.environ["PY4A_LIB"]
        ldshared+=" -L%s/Lib" % os.environ["PY4A_LIB"]
        ldshared+=" -L%s" % os.environ["GMP_LIB"]
        ldshared+=" -L."
        ldshared+=" -lc -lstdc++ -lm -Wl,--no-undefined -Wl,-z,noexecstack -lpython3 -lpython3.2m"
        ccshared = sysconfig.get_config_vars("CCSHARED")
        so_ext = "so"

        if 'LDFLAGS' in os.environ:
                ldshared += os.environ['LDFLAGS']
        if 'CFLAGS' in os.environ:
            cflags += os.environ['CFLAGS']
            ldshared += os.environ['CFLAGS']
        if 'CPPFLAGS' in os.environ:
                cpp += os.environ['CPPFLAGS']
                cflags += os.environ['CPPFLAGS']
                ldshared += os.environ['CPPFLAGS']
     
        cc_cmd = cc + ' ' + cflags
        compiler.set_executables(
            preprocessor=cpp,
            compiler=cc_cmd,
            compiler_so=cc_cmd + ' ' + ' '.join(ccshared),
            compiler_cxx=cxx,
            linker_so=ldshared,
            linker_exe=cc)

        compiler.shared_lib_extension = so_ext
    setattr(sysconfig, 'customize_compiler', customize_compiler)

    def get_config_h_filename():
        inc_dir = os.path.join(os.environ["PY4A_INC"], "..")
        config_h = 'pyconfig.h'
        return os.path.join(inc_dir, config_h)
    setattr(sysconfig, 'get_config_h_filename', get_config_h_filename)

_ext_modules = []

def read_config(file):
    f = open(file, 'r')
    lines = f.read().split('\n')   
    config_key = {}
    for e in lines:
        if e.find('=') != -1:
           param = e.split('=')
           config_key[ param[0] ] = param[1] 
    f.close()
    return config_key

print("Platform:", platform.system())
config = os.environ.get('CONFIG_FILE')
opt = {'PAIR_MOD':'yes', 'USE_PBC':'yes', 'INT_MOD':'yes','ECC_MOD':'yes'}
if config != None:
   print("Config file:", config)
   opt = read_config(config)

path = 'charm-src/'
_macros = []
_charm_version = opt.get('VERSION')

if opt.get('PAIR_MOD') == 'yes':
    if opt.get('USE_PBC') == 'yes':
        pairing_module = Extension('pairing', include_dirs = [path+'utils/'], 
                           sources = [path+'pairingmath/pairingmodule.c', path+'utils/sha1.c', path+'utils/base64.c'],
                           libraries=['pbc', 'gmp'])
    else:
        # build MIRACL based pairing module - note that this is for experimental use only
        pairing_module = Extension('pairing', include_dirs = [path+'utils/', path+'pairingmath/miracl/'], 
                           sources = [path+'pairingmath/pairingmodule2.c', path+'utils/sha1.c', path+'pairingmath/miracl/miraclwrapper.cc'],
                           libraries=['gmp','stdc++'], extra_objects=[path+'pairingmath/miracl/miracl.a'], extra_compile_args=None)
    _ext_modules.append(pairing_module)
   
if opt.get('INT_MOD') == 'yes':
   integer_module = Extension('integer', include_dirs = [path+'utils/'],
                           sources = [path+'integermath/integermodule.c', path+'utils/sha1.c', path+'utils/base64.c'], 
                           libraries=['gmp', 'crypto'])
   _ext_modules.append(integer_module)
   
if opt.get('ECC_MOD') == 'yes':
   ecc_module = Extension('ecc', include_dirs = [path+'utils/'], 
                sources = [path+'ecmath/ecmodule.c', path+'utils/sha1.c', path+'utils/base64.c'], 
                libraries=['gmp', 'crypto'])
   _ext_modules.append(ecc_module)

benchmark_module = Extension('benchmark', sources = [path+'utils/benchmarkmodule.c'])
cryptobase = Extension('cryptobase', sources = [path+'cryptobase/cryptobasemodule.c'])

aes = Extension('AES', sources = [path+'cryptobase/AES.c'])
des  = Extension('DES', include_dirs = [path+'cryptobase/libtom/'], sources = [path+'cryptobase/DES.c'])
des3  = Extension('DES3', include_dirs = [path+'cryptobase/libtom/'], sources = [path+'cryptobase/DES3.c'])
_ext_modules.extend([benchmark_module, cryptobase, aes, des, des3])

if platform.system() in ['Linux', 'Windows']:
   # add benchmark module to pairing, integer and ecc 
   if opt.get('PAIR_MOD') == 'yes': pairing_module.sources.append(path+'utils/benchmarkmodule.c')
   if opt.get('INT_MOD') == 'yes': integer_module.sources.append(path+'utils/benchmarkmodule.c')
   if opt.get('ECC_MOD') == 'yes': ecc_module.sources.append(path+'utils/benchmarkmodule.c')

patch_distutils()

setup(name = 'Charm-Crypto',
    ext_package = 'charm',
    version =  _charm_version,
    description = 'Charm is a framework for rapid prototyping of cryptosystems',
    ext_modules = _ext_modules,
    author = "J Ayo Akinyele",
    author_email = "ayo.akinyele@charm-crypto.com",
    url = "http://charm-crypto.com/",
    packages = ['charm', 'toolbox', 'compiler', 'schemes'],
    package_dir = {'charm': 'charm-src/charm'},
    package_data = {'charm':['__init__.py', 'engine/*.py'], 'toolbox':['*.py'], 'compiler':['*.py'], 'schemes':['*.py'], 'param':['*.param']},
        license = 'GPL'
     )

</pre>

### Creating the egg

In theory, the egg should be created painlessly at this point. However, setuptools has some code somewhere that automatically inserts a <code class="prettyprint">-lpython3.2mu</code> into the linking commands, which caused issues. The solution for now is to build the native modules manually, using the <code class="prettyprint">build_android.sh</code> script, as below:

<pre class="prettyprint">
#!/bin/bash

export PY4A="../python-for-android/python3-alpha/python3-src"
export PY4A_INC="${PY4A}/Include"
export PY4A_LIB="${PY4A}"
export PYTHONPATH="${PYTHONPATH}:${PY4A}/Python"
export GMP_INC="${PY4A}/../gmp-5.0.2"
export PBC_INC="${PY4A}/../pbc-0.5.12/include"
export OSSL_INC="${PY4A}/../openssl/include"
export GMP_LIB="${PY4A}/../thirdparty/lib"
export PBC_LIB=""
export OSSL_LIB="${PY4A}/../openssl/lib"
export FLAGS="-I. -Icharm-src/utils -MMD -MP -MF -fpic -ffunction-sections -funwind-tables -fstack-protector -D__ARM_ARCH_5__ -D__ARM_ARCH_5T__ -D__ARM_ARCH_5E__ -D__ARM_ARCH_5TE__ -Wno-psabi -march=armv5te -mtune=xscale -msoft-float -mthumb -Os -fomit-frame-pointer -fno-strict-aliasing -finline-limit=64 -DANDROID -Wa,--noexecstack -O2 -DNDEBUG -g -fPIC"

mkdir -p build/lib.linux-x86_64-3.2/charm/
mkdir -p build/temp.linux-x86_64-3.2/charm-src/utils/
mkdir -p build/temp.linux-x86_64-3.2/charm-src/cryptobase/
mkdir -p build/temp.linux-x86_64-3.2/charm-src/pairingmath
mkdir -p build/temp.linux-x86_64-3.2/charm-src/integermath/
mkdir -p build/temp.linux-x86_64-3.2/charm-src/ecmath/

rm -f pbc
ln -s ${PBC_INC} pbc

arm-linux-androideabi-gcc -I${PY4A_INC} -I${PY4A} -I${GMP_INC} ${FLAGS} -c charm-src/utils/sha1.c -o build/temp.linux-x86_64-3.2/charm-src/utils/sha1.o
arm-linux-androideabi-gcc -I${PY4A_INC} -I${PY4A} -I${GMP_INC} ${FLAGS} -c charm-src/utils/base64.c -o build/temp.linux-x86_64-3.2/charm-src/utils/base64.o
arm-linux-androideabi-gcc -I${PY4A_INC} -I${PY4A} -I${GMP_INC} ${FLAGS} -c charm-src/utils/benchmarkmodule.c -o build/temp.linux-x86_64-3.2/charm-src/utils/benchmarkmodule.o

arm-linux-androideabi-gcc -I${PY4A_INC} -I${PY4A} -I${GMP_INC} -I${OSSL_INC} ${FLAGS} -c charm-src/ecmath/ecmodule.c -o build/temp.linux-x86_64-3.2/charm-src/ecmath/ecmodule.o
arm-linux-androideabi-g++ -shared -lc -lstdc++ -lm -Wl,--no-undefined -Wl,-z,noexecstack -L${OSSL_LIB} -L${GMP_LIB} -lgmp -lpbc -lssl -lcrypto -L${PY4A_LIB} -lpython3.2m build/temp.linux-x86_64-3.2/charm-src/ecmath/ecmodule.o build/temp.linux-x86_64-3.2/charm-src/utils/sha1.o build/temp.linux-x86_64-3.2/charm-src/utils/base64.o build/temp.linux-x86_64-3.2/charm-src/utils/benchmarkmodule.o -o build/lib.linux-x86_64-3.2/charm/ecc.cpython-32mu.so

arm-linux-androideabi-gcc -I${PY4A_INC} -I${PY4A} -I${GMP_INC} -I${OSSL_INC} ${FLAGS} -c charm-src/integermath/integermodule.c -o build/temp.linux-x86_64-3.2/charm-src/integermath/integermodule.o
arm-linux-androideabi-g++ -shared -lc -lstdc++ -lm -Wl,--no-undefined -Wl,-z,noexecstack -L${OSSL_LIB} -L${GMP_LIB} -lgmp -lpbc -lssl -lcrypto -L${PY4A_LIB} -lpython3.2m build/temp.linux-x86_64-3.2/charm-src/integermath/integermodule.o build/temp.linux-x86_64-3.2/charm-src/utils/sha1.o build/temp.linux-x86_64-3.2/charm-src/utils/base64.o build/temp.linux-x86_64-3.2/charm-src/utils/benchmarkmodule.o -o build/lib.linux-x86_64-3.2/charm/integer.cpython-32mu.so

arm-linux-androideabi-gcc -I${PY4A_INC} -I${PY4A} -I${GMP_INC} ${FLAGS} -c charm-src/pairingmath/pairingmodule.c -o build/temp.linux-x86_64-3.2/charm-src/pairingmath/pairingmodule.o
arm-linux-androideabi-g++ -shared -lc -lstdc++ -lm -Wl,--no-undefined -Wl,-z,noexecstack -L${GMP_LIB} -lgmp -lpbc -L${PY4A_LIB} -lpython3.2m build/temp.linux-x86_64-3.2/charm-src/pairingmath/pairingmodule.o build/temp.linux-x86_64-3.2/charm-src/utils/sha1.o build/temp.linux-x86_64-3.2/charm-src/utils/base64.o build/temp.linux-x86_64-3.2/charm-src/utils/benchmarkmodule.o -o build/lib.linux-x86_64-3.2/charm/pairing.cpython-32mu.so

arm-linux-androideabi-gcc -I${PY4A_INC} -I${PY4A} ${FLAGS} -c charm-src/utils/benchmarkmodule.c -o build/temp.linux-x86_64-3.2/charm-src/utils/benchmarkmodule.o
arm-linux-androideabi-g++ -shared -lc -lstdc++ -lm -Wl,--no-undefined -Wl,-z,noexecstack -L${PY4A_LIB} -lpython3.2m build/temp.linux-x86_64-3.2/charm-src/utils/benchmarkmodule.o  -o build/lib.linux-x86_64-3.2/charm/benchmark.cpython-32mu.so

arm-linux-androideabi-gcc -I${PY4A_INC} -I${PY4A} ${FLAGS} -c charm-src/cryptobase/cryptobasemodule.c -o build/temp.linux-x86_64-3.2/charm-src/cryptobase/cryptobasemodule.o
arm-linux-androideabi-g++  -shared -lc -lstdc++ -lm -Wl,--no-undefined -Wl,-z,noexecstack -L${PY4A_LIB} -lpython3.2m build/temp.linux-x86_64-3.2/charm-src/cryptobase/cryptobasemodule.o  -o build/lib.linux-x86_64-3.2/charm/cryptobase.cpython-32mu.so

arm-linux-androideabi-gcc -I${PY4A_INC} -I${PY4A} ${FLAGS} -c charm-src/cryptobase/AES.c -o build/temp.linux-x86_64-3.2/charm-src/cryptobase/AES.o
arm-linux-androideabi-g++ -shared -lc -lstdc++ -lm -Wl,--no-undefined -Wl,-z,noexecstack -L${PY4A_LIB} -lpython3.2m build/temp.linux-x86_64-3.2/charm-src/cryptobase/AES.o -o build/lib.linux-x86_64-3.2/charm/AES.cpython-32mu.so

arm-linux-androideabi-gcc -I${PY4A_INC} -I${PY4A} ${FLAGS} -Icharm-src/cryptobase/libtom/ -c charm-src/cryptobase/DES.c -o build/temp.linux-x86_64-3.2/charm-src/cryptobase/DES.o
arm-linux-androideabi-g++ -shared -lc -lstdc++ -lm -Wl,--no-undefined -Wl,-z,noexecstack -L${PY4A_LIB} -lpython3.2m build/temp.linux-x86_64-3.2/charm-src/cryptobase/DES.o  -o build/lib.linux-x86_64-3.2/charm/DES.cpython-32mu.so

arm-linux-androideabi-gcc -I${PY4A_INC} -I${PY4A} ${FLAGS} -Icharm-src/cryptobase/libtom/ -c charm-src/cryptobase/DES3.c -o build/temp.linux-x86_64-3.2/charm-src/cryptobase/DES3.o
arm-linux-androideabi-g++ -shared -lc -lstdc++ -lm -Wl,--no-undefined -Wl,-z,noexecstack -L${PY4A_LIB} -lpython3.2m build/temp.linux-x86_64-3.2/charm-src/cryptobase/DES3.o  -o build/lib.linux-x86_64-3.2/charm/DES3.cpython-32mu.so

rm -f pbc

</pre>

Now, the egg can finally be created (it should appear in the dist folder if it succeeds):

<pre class="prettyprint">
cd ~/fresh/charm
./build_android.sh

# The following are copied from the top of the previous script
export PY4A="../python-for-android/python3-alpha/python3-src"
export PY4A_INC="${PY4A}/Include"
export PY4A_LIB="${PY4A}"
export PYTHONPATH="${PYTHONPATH}:${PY4A}/Python"
export GMP_INC="${PY4A}/../gmp-5.0.2"
export PBC_INC="${PY4A}/../pbc-0.5.12/include"
export OSSL_INC="${PY4A}/../openssl/include"
export GMP_LIB="${PY4A}/../thirdparty/lib"
export PBC_LIB=""
export OSSL_LIB="${PY4A}/../openssl/lib"

python3 setup.py bdist_egg
</pre>

### Integration with Py4A

This is fairly simple. First, copy the egg over, as below:

<pre class="prettyprint">
cd ~/fresh/python-for-android/python3-alpha/python3-src/Lib/site-packages
cp ~/fresh/charm/dist/Charm_Crypto-0.0.0-py3.2-linux-x86_64.egg .
</pre>

Now, add another entry to the <code class="prettyprint">~/fresh/python-for-android/python3-alpha/python3-src/xpack.sh</code> script so that it copies over the <code class="prettyprint">benchmark.so</code> file into the appropriate folder. Add this line right above the "#Symbolic linked libs just take up space" line:
<pre class="prettyprint">
cp ~/fresh/charm/build/lib.linux-x86_64-3.2/charm/benchmark.cpython-32mu.so python3/lib/python3.2/lib-dynload/benchmark.so
</pre>

The benchmark.so file needs to be copied over because of peculiarities with the way Charm loads that module. **NB:** This should probably be fixed upstream.

Now we just need to add an entry so that the egg can be properly loaded. Create the file <code class="prettyprint">~/fresh/python-for-android/python3-alpha/python3-src/Lib/site-packages/easy-install.pth</code> with the following contents:

<pre class="prettyprint">
import sys; sys.__plen = len(sys.path)
./Charm_Crypto-0.0.0-py3.2-linux-x86_64.egg
import sys; new=sys.path[sys.__plen:]; del sys.path[sys.__plen:]; p=getattr(sys,'__egginsert',0); sys.path[p:p]=new; sys.__egginsert = p+len(new)
</pre>

Lastly, for testing purposes, add in a script from the Charm library so that it's possible to run it on the target environment.
<pre class="prettyprint">
cd ~/fresh/python-for-android/python3-alpha/python3-src/android-scripts
cp ~/fresh/charm/schemes/dabe_aw11.py .
</pre>

Now, run a clean build of Py4A and check whether the egg appears inside the site-packages folder in python3_extras_r11.zip, as well as whether the dabe_aw11.py script appears inside the python3_scripts_r11.zip:
<pre class="prettyprint">
cd ~/fresh/python-for-android/python3-alpha
./cleanall.sh
rm python3-src/*.zip
./buildall.sh
</pre>

To confirm that the build worked, check for the following three things:

- The Charm egg should appear inside the site-packages folder in python3_extras_r11.zip
- The dabe_aw11.py script should appear inside python3_scripts_r11.zip
- The benchmark.so file should appear inside /python3/lib/python3.2/lib-dynload/ in python3_r10.zip


Deploying to the device
-----------------------

### Preliminaries

Py4A requires the files we have created previously to be available on some web server, as part of the installation process. Upload the following files to some server that the target device can access:

- <code class="prettyprint">~/fresh/python-for-android/python3-alpha/VERSIONS</code>
- <code class="prettyprint">~/fresh/python-for-android/python3-alpha/python3-src/python3_extras_r11.zip</code>
- <code class="prettyprint">~/fresh/python-for-android/python3-alpha/python3-src/python3_scripts_r11.zip</code>
- <code class="prettyprint">~/fresh/python-for-android/python3-alpha/python3-src/python3_r10.zip</code>

The following descriptions will use the [http://drop.mhlakhani.com](http://drop.mhlakhani.com) URL, replace that with your own as appropriate.

### Creating the APK

Start with a fresh workspace, and import the following projects from the <code class="prettyprint">~/fresh/python-for-android/android/</code> directory:

- Common
- InterpreterForAndroid
- Utils
- Python3ForAndroid

For each project, the ANDROID_SDK path variable (inside Properties->Java Build Path->Libraries) needs to be set so that it builds correctly. Also change the target to API 10 (Android 2.3.3).

For the Python3ForAndroid project, first set the build target to API 10 (Properties->Android), and add the other projects, as well as the code for this project, into the exported entries (Properties->Java Build Path->Order and Export). Do a clean build, and make sure it builds fine.

Now there are a few modifications that need to be made. First, we need to update the URL for the files; and we need to make sure the egg cache is writable so that the Charm egg works properly. The following diff shows the changes that need to be done:

<pre class="prettyprint">
diff -r 70d4f7c707c4 android/Python3ForAndroid/src/com/googlecode/python3forandroid/Python3Descriptor.java
--- a/android/Python3ForAndroid/src/com/googlecode/python3forandroid/Python3Descriptor.java	Sun Apr 22 17:44:01 2012 +1000
+++ b/android/Python3ForAndroid/src/com/googlecode/python3forandroid/Python3Descriptor.java	Tue May 08 17:12:31 2012 +0500
@@ -42,7 +42,7 @@
   private static final String ENV_EGGS = "PYTHON_EGG_CACHE";
   private static final String ENV_USERBASE = "PYTHONUSERBASE";
   // static final String BASE_URL = "http://python-for-android.googlecode.com/files";
-  static final String BASE_URL = "http://www.mithril.com.au/android";
+  static final String BASE_URL = "http://drop.mhlakhani.com";
   private static final int LATEST_VERSION = 5;
   private int cache_scripts_version = -1;
   private SharedPreferences mPreferences;
@@ -159,6 +159,10 @@
       FileUtils.chmod(context.getCacheDir(), 0777); // Make sure this is writable.
     } catch (Exception e) {
     }
+    try {
+      FileUtils.chmod(new File(getHome(context), "python3/lib/python3.2/lib-dynload"), 0777);
+    } catch (Exception e) {
+    }
     values.put("HOME", Environment.getExternalStorageDirectory().getAbsolutePath());
     for (String k : values.keySet()) {
       Log.d(k + " : " + values.get(k));


diff -r 70d4f7c707c4 android/Python3ForAndroid/src/com/googlecode/python3forandroid/Python3Main.java
--- a/android/Python3ForAndroid/src/com/googlecode/python3forandroid/Python3Main.java	Sun Apr 22 17:44:01 2012 +1000
+++ b/android/Python3ForAndroid/src/com/googlecode/python3forandroid/Python3Main.java	Tue May 08 17:12:31 2012 +0500
@@ -832,7 +832,7 @@
       URL url;
       try {
         // url = new URL("http://python-for-android.googlecode.com/hg/python3-alpha/VERSIONS");
-        url = new URL("http://www.mithril.com.au/android/VERSIONS");
+        url = new URL("http://drop.mhlakhani.com/VERSIONS");
         Properties p = new Properties();
         p.load(url.openStream());
         if (p.containsKey("PY34A_VERSION")) {
</pre>

After this modification is made, do a clean build, and then export a signed APK using Android Tools->Export Signed Application Package. Place the .apk in <code class="prettyprint">~/fresh</code>

### Final Deployment
<a name="final"></a>Py4A runs under SL4A. Download that APK from [here](https://android-scripting.googlecode.com/files/sl4a_r5.apk) and place it in <code class="prettyprint">~/fresh</code>

If you just want to run Charm without having to go through the whole build process, you can also grab a pre-prepared version of the APK from [this link](http://drop.mhlakhani.com/Python3ForAndroid.apk).

For testing purposes, use an emulator image for Android 10 (these steps could potentially be run on a hardware device too). Create an appropriate image, and launch the emulator. Using adb, install the applications, as below:

<pre class="prettyprint">
cd ~/fresh
adb install sl4a_r5.apk
adb install Python3ForAndroid.apk
</pre>

Now, in the emulator, open the Python3ForAndroid application, and click the "Install" button at the top. It will download the previously created zip files and install them; the process may take a while.

Once that is done, open the SL4A application, and run the <code class="prettyprint">dabe_aw11.py</code> script. It should run correctly, and show a "Successful Decryption!" message.
