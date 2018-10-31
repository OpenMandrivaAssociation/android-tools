Name: android-tools
Epoch: 1
# In 9.0, the mke2fs tool is gone. We can't
# update past 8.1.0_r* until we stop relying
# on that tool for Dragonboard and Nitrogen8M builds.
Version: 8.1.0_r48
Release: 2
# https://android.googlesource.com/platform/system/core
Source0: core-%{version}.tar.xz
# https://android.googlesource.com/platform/system/extras
Source1: extras-%{version}.tar.xz
# https://android.googlesource.com/platform/external/e2fsprogs
Source2: e2fsprogs-%{version}.tar.xz
# Not officially supported, but very useful for working
# with phones that don't have a full source tree release...
# https://github.com/ggrandou/abootimg
Source3: abootimg-20181011.tar.xz
# Useful for generating Android-style boot.img images containing
# non-Android kernels
# git://codeaurora.org/quic/kernel/skales
Source4: skales-20180909.tar.xz
Source100: package-source.sh
Summary: Tools for working with/on Android
URL: http://android.googlesource.com/
License: Apache 2.0
Group: Development/Tools
BuildRequires: pkgconfig(libusb-1.0)
BuildRequires: pkgconfig(zlib)
BuildRequires: pkgconfig(libcrypto)
BuildRequires: pkgconfig(blkid)
BuildRequires: selinux-static-devel
BuildRequires: gtest-devel
Patch0: adb-system-libraries.patch
Patch1: libbase-clang-5.0.patch
Patch2: libcrypto_utils-openssl-1.1.patch
Patch3: adb-system-openssl.patch
Patch4: make_ext4fs-add-keep-uids-option.patch
# System mke2fs won't work because fastboot uses custom
# options such as android_sparse
Patch5: fastboot-use-custom-mke2fs.patch
Patch6: adb-glibc-2.28.patch
# https://bugs.launchpad.net/ubuntu/+source/abootimg/+bug/1606633
Patch7: https://launchpadlibrarian.net/275172896/0001-Fix-extraction-of-stage2-image.patch

%description
This package provides various tools for working with (and on) Android devices:
adb -- The Android Debug Bridge client
fastboot -- A tool for talking to Android's "fastboot" bootloader
simg2img -- A tool for converting Android sparse images into regular
            filesystems
img2simg -- A tool for converting regular filesystem images to Android
            sparse images that can be used with fastboot
append2simg -- A tool to append to a sparse image
make_ext4fs -- A tool to generate ext4 sparse images

%prep
%setup -qn platform -b 1 -b 2 -b 3 -b 4
cd ..
%autopatch -p0

%build
cd system/core/libsparse
for i in backed_block output_file sparse sparse_crc32 sparse_err; do
	%{__cc} %{optflags} -DHOST -D_FILE_OFFSET_BITS=64 -D_LARGEFILE64_SOURCE=1 -D_LARGEFILE_SOURCE=1 -Iinclude -o $i.o -c $i.c
done
for i in sparse_read; do
	%{__cxx} %{optflags} -DHOST -D_FILE_OFFSET_BITS=64 -D_LARGEFILE64_SOURCE=1 -D_LARGEFILE_SOURCE=1 -Iinclude -I../base/include -o $i.o -c $i.cpp
done
ar cru libsparse.a *.o
ranlib libsparse.a

# We only need a small subset of libbase -- the other files are "missing" intentionally
cd ../base
for i in file logging parsenetaddress stringprintf strings errors_unix test_utils; do
	%{__cxx} %{optflags} -std=gnu++14 -D_FILE_OFFSET_BITS=64 -D_LARGEFILE64_SOURCE=1 -D_LARGEFILE_SOURCE=1 -Iinclude -I../include -o $i.o -c $i.cpp
done
ar cru libbase.a *.o
ranlib libbase.a

cd ../libsparse
for i in simg2img img2simg append2simg; do
	%{__cc} %{optflags} -DHOST -D_FILE_OFFSET_BITS=64 -D_LARGEFILE64_SOURCE=1 -D_LARGEFILE_SOURCE=1 -Iinclude -o $i.o -c $i.c
done
%{__cxx} %{optflags} -DHOST -D_FILE_OFFSET_BITS=64 -D_LARGEFILE64_SOURCE=1 -D_LARGEFILE_SOURCE=1 -Iinclude -o simg2img simg2img.o $(pkg-config --libs zlib) libsparse.a ../base/libbase.a
%{__cxx} %{optflags} -DHOST -D_FILE_OFFSET_BITS=64 -D_LARGEFILE64_SOURCE=1 -D_LARGEFILE_SOURCE=1 -Iinclude -o img2simg img2simg.o $(pkg-config --libs zlib) libsparse.a ../base/libbase.a
%{__cxx} %{optflags} -DHOST -D_FILE_OFFSET_BITS=64 -D_LARGEFILE64_SOURCE=1 -D_LARGEFILE_SOURCE=1 -Iinclude -o append2simg append2simg.o $(pkg-config --libs zlib) libsparse.a ../base/libbase.a

# We only need a small subset of libcutils -- the other files are "missing" intentionally
cd ../libcutils
for i in load_file socket_local_client_unix socket_network_client_unix socket_local_server_unix sockets_unix socket_inaddr_any_server_unix sockets threads fs_config canned_fs_config android_get_control_file; do
	if [ -e $i.c ]; then
		%{__cc} -std=gnu11 %{optflags} -DHOST -D_FILE_OFFSET_BITS=64 -D_LARGEFILE64_SOURCE=1 -D_LARGEFILE_SOURCE=1 -Dchar16_t=uint16_t -Iinclude -I../include -o $i.o -c $i.c
	else
		%{__cxx} -std=gnu++14 %{optflags} -DHOST -D_FILE_OFFSET_BITS=64 -D_LARGEFILE64_SOURCE=1 -D_LARGEFILE_SOURCE=1 -Dchar16_t=uint16_t -Iinclude -I../include -o $i.o -c $i.cpp
	fi
done
ar cru libcutils.a *.o
ranlib libcutils.a

# We only need a small subset of libutils -- the other files are "missing" intentionally
cd ../libutils
for i in FileMap; do
	%{__cxx} -std=gnu++14 %{optflags} -DHOST -D_FILE_OFFSET_BITS=64 -D_LARGEFILE64_SOURCE=1 -D_LARGEFILE_SOURCE=1 -Iinclude -I../include -o $i.o -c $i.cpp
done
ar cru libutils.a *.o
ranlib libutils.a

# We only need a small subset of liblog -- the other files are "missing" intentionally
cd ../liblog
for i in log_event_write fake_log_device log_event_list logger_write config_write logger_lock fake_writer logger_name local_logger stderr_write logprint config_read; do
	%{__cc} %{optflags} -std=gnu11 -D_FILE_OFFSET_BITS=64 -D_LARGEFILE64_SOURCE=1 -D_LARGEFILE_SOURCE=1 -DLIBLOG_LOG_TAGS=1005 -DFAKE_LOG_DEVICE=1 -D_GNU_SOURCE -Iinclude -I../include -o $i.o -c $i.c
done
ar cru liblog.a *.o
ranlib liblog.a

cd ../libziparchive
for i in zip_archive.cc; do
	%{__cxx} -std=gnu++14 %{optflags} -D_FILE_OFFSET_BITS=64 -D_LARGEFILE64_SOURCE=1 -D_LARGEFILE_SOURCE=1 -o ${i/.cc/.o} -c $i -I. -Iinclude -I../include -I../base/include
done
ar cru libziparchive.a *.o
ranlib libziparchive.a

cd ../libcrypto_utils
for i in *.c; do
	%{__cc} -std=gnu11 %{optflags} -D_FILE_OFFSET_BITS=64 -D_LARGEFILE64_SOURCE=1 -D_LARGEFILE_SOURCE=1 -o ${i/.c/.o} -c $i -Iinclude
done
ar cru libcrypto_utils.a *.o
ranlib libcrypto_utils.a

cd ../../extras/ext4_utils
for i in make_ext4fs ext4fixup ext4_utils allocate contents extent indirect sha1 wipe crc16 ext4_sb; do
	%{__cc} %{optflags} -DANDROID -DHOST -D_FILE_OFFSET_BITS=64 -D_LARGEFILE64_SOURCE=1 -D_LARGEFILE_SOURCE=1 -std=gnu11 -Iinclude -I../../core/include -I../../core/libsparse/include -o $i.o -c $i.c
done
ar cru libext4_utils.a *.o
ranlib libext4_utils.a
pwd
%{__cc} %{optflags} -DANDROID -DHOST -D_FILE_OFFSET_BITS=64 -D_LARGEFILE64_SOURCE=1 -D_LARGEFILE_SOURCE=1 -o make_ext4fs make_ext4fs_main.c libext4_utils.a -Iinclude -I../../core/libcutils/include -I../../core/libsparse/include -I../../core/include $(pkg-config --libs libselinux) $(pkg-config --libs zlib) ../../core/libsparse/libsparse.a ../../core/libcutils/libcutils.a ../../core/liblog/liblog.a -lpthread

cd ../../core/adb
for i in adb adb_auth_host adb_io adb_listeners adb_trace adb_utils fdevent sockets socket_spec sysdeps/errno transport transport_local transport_usb sysdeps_unix client/usb_dispatch client/usb_libusb client/usb_linux adb_client bugreport client/main console commandline diagnose_usb file_sync_client line_printer services shell_service_protocol transport_mdns_unsupported sysdeps/posix/network; do
	%{__cxx} %{optflags} -D_FILE_OFFSET_BITS=64 -D_LARGEFILE64_SOURCE=1 -D_LARGEFILE_SOURCE=1 -DADB_HOST=1 -D_GNU_SOURCE=1 -fvisibility=hidden -std=gnu++14 -I../base/include -I../include -I../libcrypto_utils/include -I. -DADB_VERSION=\"26.1.0-eng.bero.$(date +%%Y%%m%%d.%%H%%M%%S)\" -DADB_REVISION='"%{version}-%{release}"' -o $i.o -c $i.cpp
done
%{__cxx} %{optflags} -D_FILE_OFFSET_BITS=64 -D_LARGEFILE64_SOURCE=1 -D_LARGEFILE_SOURCE=1 -fvisibility=hidden -std=gnu++14 -o adb *.o client/*.o sysdeps/*.o sysdeps/*/*.o -lpthread $(pkg-config --libs libcrypto) ../base/libbase.a ../libcutils/libcutils.a $(pkg-config --libs libusb-1.0) ../libcrypto_utils/libcrypto_utils.a

cd ../fastboot
for i in bootimg_utils engine fastboot fs protocol socket tcp udp util usb_linux; do
	%{__cxx} %{optflags} -std=gnu++14 -DFASTBOOT_VERSION=\"26.1.0-eng.bero.$(date +%%Y%%m%%d.%%H%%M%%S)\" -DFASTBOOT_REVISION='"%{version}-%{release}"' -D_FILE_OFFSET_BITS=64 -D_LARGEFILE64_SOURCE=1 -D_LARGEFILE_SOURCE=1 -D_GNU_SOURCE -I../base/include -I../include -I../adb -I../libsparse/include -I../mkbootimg -I../../extras/ext4_utils/include -I../../extras/f2fs_utils -I../libziparchive/include -o $i.o -c $i.cpp
done
%{__cxx} -std=gnu++14 %{optflags} -D_FILE_OFFSET_BITS=64 -D_LARGEFILE64_SOURCE=1 -D_LARGEFILE_SOURCE=1 -fvisibility=hidden -o fastboot -lz -lpthread *.o ../adb/diagnose_usb.o ../../extras/ext4_utils/libext4_utils.a ../libcutils/libcutils.a ../libsparse/libsparse.a ../libziparchive/libziparchive.a ../base/libbase.a ../libutils/libutils.a ../liblog/liblog.a

cd ../../../external/e2fsprogs/lib/ext2fs
# Get rid of bits we don't need...
rm -f bmove.c dosio.c irel_ma.c nt_io.c tst_*.c gen_crc32ctable.c tdbtool.c
for i in *.c; do
	%{__cc} %{optflags} -DANDROID -DHOST -D_FILE_OFFSET_BITS=64 -D_LARGEFILE64_SOURCE=1 -D_LARGEFILE_SOURCE=1 -std=gnu11 -I. -I.. -I../../../../system/core/libsparse/include -o ${i/.c/.o} -c $i
done
ar cru libext2fs.a *.o
ranlib libext2fs.a

cd ../et
for i in *.c; do
	%{__cc} %{optflags} -DANDROID -DHOST -D_FILE_OFFSET_BITS=64 -D_LARGEFILE64_SOURCE=1 -D_LARGEFILE_SOURCE=1 -std=gnu11 -I. -I.. -o ${i/.c/.o} -c $i
done
ar cru libcom_err.a *.o
ranlib libcom_err.a

cd ../e2p
for i in *.c; do
	%{__cc} %{optflags} -DANDROID -DHOST -D_FILE_OFFSET_BITS=64 -D_LARGEFILE64_SOURCE=1 -D_LARGEFILE_SOURCE=1 -std=gnu11 -I. -I.. -o ${i/.c/.o} -c $i
done
ar cru libe2p.a *.o
ranlib libe2p.a

cd ../uuid
rm -f gen_uuid_nt.c
for i in *.c; do
	%{__cc} %{optflags} -DANDROID -DHOST -D_FILE_OFFSET_BITS=64 -D_LARGEFILE64_SOURCE=1 -D_LARGEFILE_SOURCE=1 -std=gnu11 -I. -I.. -o ${i/.c/.o} -c $i
done
ar cru libuuid.a *.o
ranlib libuuid.a

cd ../blkid
for i in *.c; do
	%{__cc} %{optflags} -DANDROID -DHOST -D_FILE_OFFSET_BITS=64 -D_LARGEFILE64_SOURCE=1 -D_LARGEFILE_SOURCE=1 -std=gnu11 -I. -I.. -o ${i/.c/.o} -c $i
done
ar cru libblkid.a *.o
ranlib libblkid.a

cd ../support
for i in *.c; do
	%{__cc} %{optflags} -DANDROID -DHOST -D_FILE_OFFSET_BITS=64 -D_LARGEFILE64_SOURCE=1 -D_LARGEFILE_SOURCE=1 -std=gnu11 -I. -I.. -o ${i/.c/.o} -c $i
done
ar cru libsupport.a *.o
ranlib libsupport.a

cd ../../misc
# create_inode.c's copy_file_range isn't what unistd.h thinks it is
sed -i -e 's,copy_file_range,e2_copy_file_range,g' create_inode.c
for i in mke2fs util mk_hugefiles default_profile create_inode; do
	%{__cc} %{optflags} -DANDROID -DHOST -D_FILE_OFFSET_BITS=64 -D_LARGEFILE64_SOURCE=1 -D_LARGEFILE_SOURCE=1 -std=gnu11 -I../lib -I../lib/ext2fs -I../misc -o $i.o -c $i.c
done
%{__cxx} %{optflags} -DANDROID -DHOST -D_FILE_OFFSET_BITS=64 -D_LARGEFILE64_SOURCE=1 -D_LARGEFILE_SOURCE=1 -Iinclude -I../../core/include -I../../core/libsparse/include -o mke2fs *.o ../lib/ext2fs/*.o ../lib/et/libcom_err.a ../lib/support/libsupport.a ../lib/blkid/libblkid.a ../lib/e2p/libe2p.a ../lib/uuid/libuuid.a ../../../system/core/libsparse/libsparse.a ../../../system/core/libcutils/libcutils.a ../../../system/core/liblog/liblog.a ../../../system/core/base/libbase.a -lz

cd ../contrib/android
cp ../../misc/create_inode.c .
for i in e2fsdroid block_range create_inode fsmap block_list base_fs perms basefs_allocator hashmap; do
	%{__cc} %{optflags} -DANDROID -DHOST -D_FILE_OFFSET_BITS=64 -D_LARGEFILE64_SOURCE=1 -D_LARGEFILE_SOURCE=1 -std=gnu11 -I../../lib -I../../lib/ext2fs -I../../misc -I../../../../system/core/libcutils/include -I../../../../system/core/libsparse/include -o $i.o -c $i.c
done
%{__cxx} %{optflags} -DANDROID -DHOST -D_FILE_OFFSET_BITS=64 -D_LARGEFILE64_SOURCE=1 -D_LARGEFILE_SOURCE=1 -Iinclude -I../../core/include -I../../core/libsparse/include -o e2fsdroid *.o ../../lib/ext2fs/libext2fs.a ../../../../system/core/libsparse/libsparse.a ../../../../system/core/libcutils/libcutils.a ../../../../system/core/liblog/liblog.a ../../lib/et/libcom_err.a -lselinux ../../../../system/core/base/libbase.a -lz -lpthread

pwd
cd ../../../../../abootimg
make CFLAGS="%{optflags}" LDFLAGS="%{optflags}"

%install
mkdir -p %{buildroot}%{_bindir}
install -c -m755 system/core/libsparse/simg2img %{buildroot}%{_bindir}/
install -c -m755 system/core/libsparse/img2simg %{buildroot}%{_bindir}/
install -c -m755 system/core/libsparse/append2simg %{buildroot}%{_bindir}/

install -c -m755 system/extras/ext4_utils/make_ext4fs %{buildroot}%{_bindir}/

install -c -m755 system/core/adb/adb %{buildroot}%{_bindir}/
install -c -m755 system/core/fastboot/fastboot %{buildroot}%{_bindir}/

install -c -m755 external/e2fsprogs/misc/mke2fs %{buildroot}%{_bindir}/mke2fsdroid
install -c -m755 external/e2fsprogs/contrib/android/e2fsdroid %{buildroot}%{_bindir}/

install -c -m755 ../abootimg/abootimg %{buildroot}%{_bindir}/
install -c -m755 ../abootimg/abootimg-pack-initrd %{buildroot}%{_bindir}/
install -c -m755 ../abootimg/abootimg-unpack-initrd %{buildroot}%{_bindir}/

install -c -m755 ../skales/dtbTool %{buildroot}%{_bindir}/
install -c -m755 ../skales/mkbootimg %{buildroot}%{_bindir}/

%files
%{_bindir}/*
