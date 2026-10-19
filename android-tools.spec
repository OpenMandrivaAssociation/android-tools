Name: android-tools
Version: 37.0.0p1
Release: 1
# https://android.googlesource.com/platform/system/core
Source0: https://github.com/nmeum/android-tools/releases/download/%{version}/android-tools-%{version}.tar.xz
# Not officially supported, but very useful for working
# with phones that don't have a full source tree release...
# https://github.com/ggrandou/abootimg
Source1: abootimg-20181011.tar.xz
# Useful for generating Android-style boot.img images containing
# non-Android kernels
# git://codeaurora.org/quic/kernel/skales
Source2: skales-20180909.tar.xz
Source3: https://src.fedoraproject.org/rpms/android-tools/raw/rawhide/f/51-android.rules
Source4: https://src.fedoraproject.org/rpms/android-tools/raw/rawhide/f/adb.service
Patch0: 0001-Fix-extraction-of-stage2-image.patch
Summary: Tools for working with/on Android
URL: https://android.googlesource.com/
License: Apache 2.0
Group: Development/Tools
BuildRequires: pkgconfig(protobuf)
BuildRequires: cmake(absl)
BuildRequires: cmake(fmt)
BuildRequires: pkgconfig(libbrotlicommon)
BuildRequires: pkgconfig(libbrotlidec)
BuildRequires: pkgconfig(libbrotlienc)
BuildRequires: pkgconfig(libzstd)
BuildRequires: pkgconfig(liblz4)
BuildRequires: pkgconfig(libpcre2-8)
BuildRequires: pkgconfig(libusb-1.0)
BuildRequires: pkgconfig(zlib)
BuildRequires: pkgconfig(libcrypto)
BuildRequires: pkgconfig(blkid)
BuildRequires: systemd
BuildRequires: pkgconfig(libsystemd)
BuildRequires: pkgconfig(libunwind-generic)
BuildRequires: selinux-static-devel
BuildRequires: gtest-devel
BuildRequires: perl
BuildRequires: cmake ninja make

%description
This package provides various tools for working with (and on) Android devices:
adb -- The Android Debug Bridge client
fastboot -- A tool for talking to Android's "fastboot" bootloader
simg2img -- A tool for converting Android sparse images into regular
            filesystems
img2simg -- A tool for converting regular filesystem images to Android
            sparse images that can be used with fastboot
append2simg -- A tool to append to a sparse image

%prep
%autosetup -p1 -a 1
tar xf %{S:2}
# clang 23 no longer sees uint8_t via transitive headers.
# Do not use -include cstdint globally: that pulls _GNU_SOURCE before
# posix_strerror_r.cpp can #undef it, so GNU strerror_r (char *) wins.
grep -q cstdint vendor/libbase/hex.cpp || sed -i '1i#include <cstdint>' vendor/libbase/hex.cpp
grep -q cstdint vendor/libziparchive/include/ziparchive/zip_writer.h || \
	sed -i '1i#include <cstdint>' vendor/libziparchive/include/ziparchive/zip_writer.h

# Rust mDNS pulls crates that are not in this tarball. Leave it off.
%cmake -G Ninja \
	-DBUILD_SHARED_LIBS:BOOL=OFF \
	-DBUILD_STATIC_LIBS:BOOL=ON \
	-DANDROID_TOOLS_ADB_ENABLE_MDNS:BOOL=OFF

%build
%ninja_build -C build
cd abootimg
make CFLAGS="%{optflags}"

%install
%ninja_install -C build

install -c -m 755 abootimg/abootimg %{buildroot}%{_bindir}/
install -c -m 755 abootimg/abootimg-pack-initrd %{buildroot}%{_bindir}/
install -c -m 755 abootimg/abootimg-unpack-initrd %{buildroot}%{_bindir}/

install -c -m 755 skales/dtbTool %{buildroot}%{_bindir}/
install -c -m 755 skales/mkbootimg %{buildroot}%{_bindir}/

mkdir -p %{buildroot}/lib/udev/rules.d
install -c -m 644 %{S:3} %{buildroot}/lib/udev/rules.d/

mkdir -p %{buildroot}%{_unitdir}
install -c -m 644 %{S:4} %{buildroot}%{_unitdir}/

install -d -m 0775 %{buildroot}%{_sharedstatedir}/adb

%files
%{_bindir}/*
%{_datadir}/android-tools
%{_datadir}/bash-completion/completions/{adb,fastboot}
%{_datadir}/zsh/site-functions/_adb
%{_datadir}/zsh/site-functions/_fastboot
%{_unitdir}/*.service
%dir %{_sharedstatedir}/adb
/lib/udev/rules.d/*
%{_mandir}/man1/adb.1*
