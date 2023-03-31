Name: android-tools
# In 9.0, the make_ext4tfs tool is gone. We can't
# update past 8.1.0_r* until we stop relying
# on that tool for Dragonboard and Nitrogen8M builds.
Version: 34.0.0
Release: 3
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
Patch1: android-tools-34-protobuf-22.1.patch
Summary: Tools for working with/on Android
URL: http://android.googlesource.com/
License: Apache 2.0
Group: Development/Tools
BuildRequires: pkgconfig(protobuf)
BuildRequires: cmake(absl)
BuildRequires: pkgconfig(libbrotlidec)
BuildRequires: pkgconfig(libbrotlienc)
BuildRequires: pkgconfig(libzstd)
BuildRequires: pkgconfig(liblz4)
BuildRequires: pkgconfig(libusb-1.0)
BuildRequires: pkgconfig(zlib)
BuildRequires: pkgconfig(libcrypto)
BuildRequires: pkgconfig(blkid)
BuildRequires: systemd
BuildRequires: pkgconfig(libsystemd)
BuildRequires: selinux-static-devel
BuildRequires: gtest-devel
BuildRequires: golang perl
BuildRequires: cmake ninja

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
%autosetup -p1 -a 1
tar xf %{S:2}

%cmake -G Ninja \
	-DBUILD_SHARED_LIBS:BOOL=OFF \
	-DBUILD_STATIC_LIBS:BOOL=ON

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
%{_unitdir}/*.service
%dir %{_sharedstatedir}/adb
/lib/udev/rules.d/*
