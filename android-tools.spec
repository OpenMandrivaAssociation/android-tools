Name: android-tools
Version: 7.1.2_r11
Release: 1
# https://android.googlesource.com/platform/system/core
Source0: core-%{version}.tar.xz
# https://android.googlesource.com/platform/system/extras
Source1: extras-%{version}.tar.xz
Summary: Tools for working with/on Android
URL: http://android.googlesource.com/
License: Apache 2.0
Group: Development/Tools
BuildRequires: pkgconfig(zlib)
BuildRequires: pkgconfig(libcrypto)
BuildRequires: selinux-static-devel
BuildRequires: gtest-devel
Patch0: adb-clang-4.0.patch
Patch1: libbase-clang-4.0.patch
Patch2: adb-openssl-1.1.patch
Patch3: libziparchive-clang-4.0.patch

%description
This package provides various tools for working with (and on) Android devices:
adb -- The Android Debug Bridge client
fastboot -- A tool for talking to Android's "fastboot" bootloader
simg2img -- A tool for converting Android sparse images into regular
            filesystems
img2simg -- A tool for converting regular filesystem images to Android
            sparse images that can be used with fastboot
append2simg -- A tool to append to a sparse image
ext2simg -- A tool to create fastboot compatible sparse images from
            ext2/ext3/ext4 images
make_ext4fs -- A tool to generate ext4 sparse images

%prep
%setup -qn platform -b 1
%apply_patches

%build
cd system/core/libsparse
for i in backed_block output_file sparse sparse_crc32 sparse_err sparse_read; do
	%{__cc} %{optflags} -DHOST -Iinclude -o $i.o -c $i.c
done
ar cru libsparse.a *.o
ranlib libsparse.a
%{__cc} %{optflags} -DHOST -Iinclude -o simg2img simg2img.c $(pkg-config --libs zlib) libsparse.a
%{__cc} %{optflags} -DHOST -Iinclude -o img2simg img2simg.c $(pkg-config --libs zlib) libsparse.a
%{__cc} %{optflags} -DHOST -Iinclude -o append2simg append2simg.c $(pkg-config --libs zlib) libsparse.a

# We only need a small subset of libcutils -- the other files are "missing" intentionally
cd ../libcutils
for i in load_file socket_local_client_unix socket_loopback_client_unix socket_network_client_unix socket_loopback_server_unix socket_local_server_unix sockets_unix socket_inaddr_any_server_unix sockets threads fs_config canned_fs_config; do
	if [ -e $i.c ]; then
		%{__cc} -std=gnu11 %{optflags} -DHOST -Dchar16_t=uint16_t -Iinclude -I../include -o $i.o -c $i.c
	else
		%{__cxx} -std=gnu++14 %{optflags} -DHOST -Dchar16_t=uint16_t -Iinclude -I../include -o $i.o -c $i.cpp
	fi
done
ar cru libcutils.a *.o
ranlib libcutils.a

# We only need a small subset of libutils -- the other files are "missing" intentionally
cd ../libutils
for i in FileMap; do
	%{__cxx} -std=gnu++14 %{optflags} -DHOST -Iinclude -I../include -o $i.o -c $i.cpp
done
ar cru libutils.a *.o
ranlib libutils.a

# We only need a small subset of libbase -- the other files are "missing" intentionally
cd ../base
for i in file logging parsenetaddress stringprintf strings errors_unix; do
	%{__cxx} %{optflags} -std=gnu++14 -Iinclude -I../include -o $i.o -c $i.cpp
done
ar cru libbase.a *.o
ranlib libbase.a

# We only need a small subset of liblog -- the other files are "missing" intentionally
cd ../liblog
for i in log_event_write fake_log_device log_event_list logger_write config_write logger_lock fake_writer logger_name; do
	%{__cc} %{optflags} -std=gnu11 -DLIBLOG_LOG_TAGS=1005 -DFAKE_LOG_DEVICE=1 -D_GNU_SOURCE -Iinclude -I../include -o $i.o -c $i.c
done
ar cru liblog.a *.o
ranlib liblog.a

cd ../libziparchive
for i in zip_archive.cc; do
	%{__cxx} -std=gnu++14 %{optflags} -o ${i/.cc/.o} -c $i -I. -I../include -I../base/include
done
ar cru libziparchive.a *.o
ranlib libziparchive.a

cd ../../extras/ext4_utils
for i in make_ext4fs ext4fixup ext4_utils allocate contents extent indirect sha1 wipe crc16 ext4_sb ext2simg; do
	%{__cc} %{optflags} -DANDROID -DHOST -std=gnu11 -Iinclude -I../../core/include -I../../core/libsparse/include -o $i.o -c $i.c
done
ar cru libext4_utils.a $(ls *.o |grep -v ext2simg.o)
ranlib libext4_utils.a
%{__cc} %{optflags} -DANDROID -DHOST -o ext2simg ext2simg.o -I../../core/libsparse/include $(pkg-config --libs zlib) ../../core/libsparse/libsparse.a libext4_utils.a
%{__cc} %{optflags} -DANDROID -DHOST -o make_ext4fs make_ext4fs_main.c libext4_utils.a -I../../core/libsparse/include -I../../core/include $(pkg-config --libs libselinux) $(pkg-config --libs zlib) ../../core/libsparse/libsparse.a ../../core/libcutils/libcutils.a ../../core/liblog/liblog.a -lpthread

cd ../../core/adb
for i in adb adb_auth adb_auth_host adb_io adb_listeners adb_trace adb_utils fdevent sockets transport transport_local transport_usb get_my_path_linux sysdeps_unix usb_linux adb_client bugreport client/main console commandline diagnose_usb file_sync_client line_printer services shell_service_protocol; do
	%{__cxx} %{optflags} -DADB_HOST=1 -D_GNU_SOURCE=1 -fvisibility=hidden -std=gnu++14 -I../base/include -I../include -I. -DADB_REVISION='"%{version}-%{release}"' -o $i.o -c $i.cpp
done
%{__cxx} %{optflags} -fvisibility=hidden -std=gnu++14 -o adb *.o client/*.o -lpthread $(pkg-config --libs libcrypto) ../base/libbase.a ../libcutils/libcutils.a

cd ../fastboot
for i in protocol engine bootimg_utils fastboot util fs usb_linux util_linux socket tcp udp; do
	%{__cxx} %{optflags} -std=gnu++14 -DFASTBOOT_REVISION='"%{version}-%{release}"' -D_GNU_SOURCE -I../base/include -I../include -I../adb -I../libsparse/include -I../mkbootimg -I../../extras/ext4_utils -I../../extras/f2fs_utils -o $i.o -c $i.cpp
done
%{__cxx} -std=gnu++14 %{optflags} -fvisibility=hidden -o fastboot -lz -lpthread *.o ../adb/diagnose_usb.o ../../extras/ext4_utils/libext4_utils.a ../libcutils/libcutils.a ../libsparse/libsparse.a ../libziparchive/libziparchive.a ../base/libbase.a ../libutils/libutils.a ../liblog/liblog.a

%install
mkdir -p %{buildroot}%{_bindir}
install -c -m755 system/core/libsparse/simg2img %{buildroot}%{_bindir}/
install -c -m755 system/core/libsparse/img2simg %{buildroot}%{_bindir}/
install -c -m755 system/core/libsparse/append2simg %{buildroot}%{_bindir}/

install -c -m755 system/extras/ext4_utils/ext2simg %{buildroot}%{_bindir}/
install -c -m755 system/extras/ext4_utils/make_ext4fs %{buildroot}%{_bindir}/

install -c -m755 system/core/adb/adb %{buildroot}%{_bindir}/
install -c -m755 system/core/fastboot/fastboot %{buildroot}%{_bindir}/

%files
%{_bindir}/*
