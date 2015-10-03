%define date 20141219
%define git_commit 8393e50
%define packdname core-%{git_commit}
%define extras_git_commit 1e7d4f3
%define extras_packdname extras-%{extras_git_commit}

Name:          android-tools
Version:       %{date}git%{git_commit}
Release:       1
Summary:       Android platform tools(adb, fastboot)
# The entire source code is ASL 2.0 except fastboot/ which is BSD
License:       ASL 2.0 and (ASL 2.0 and BSD)
URL:           http://developer.android.com/guide/developing/tools/
#  using git archive since upstream hasn't created tarballs. 
#  git archive --format=tar --prefix=%%{packdname}/ %%{git_commit} adb fastboot libzipfile libcutils libmincrypt libsparse mkbootimg include/cutils include/zipfile include/mincrypt include/utils include/private | xz  > %%{packdname}.tar.xz
#  https://android.googlesource.com/platform/system/core.git
#  git archive --format=tar --prefix=extras/ %%{extras_git_commit} ext4_utils f2fs_utils | xz  > %%{extras_packdname}.tar.xz
#  https://android.googlesource.com/platform/system/extras.git
Source0:       %{packdname}.tar.xz
Source1:       %{extras_packdname}.tar.xz
Source2:       core-Makefile
Source3:       adb-Makefile
Source4:       fastboot-Makefile
Source5:       51-android.rules
Source6:       adb.service
# None of the code *we* compile uses anything from selinux/android.h, but 
# other code may, so not upstreaming these patches
Patch1:        0001-Remove-android-selinux-header.patch
BuildRequires: zlib-devel
BuildRequires: openssl-devel
BuildRequires: selinux-devel
BuildRequires: f2fs-tools-devel

Provides:      adb
Provides:      fastboot

%description

The Android Debug Bridge (ADB) is used to:

- keep track of all Android devices and emulators instances
  connected to or running on a given host developer machine

- implement various control commands (e.g. "adb shell", "adb pull", etc.)
  for the benefit of clients (command-line users, or helper programs like
  DDMS). These commands are what is called a 'service' in ADB.

Fastboot is used to manipulate the flash partitions of the Android phone. 
It can also boot the phone using a kernel image or root filesystem image 
which reside on the host machine rather than in the phone flash. 
In order to use it, it is important to understand the flash partition 
layout for the phone.
The fastboot program works in conjunction with firmware on the phone 
to read and write the flash partitions. It needs the same USB device 
setup between the host and the target phone as adb.

%prep
%setup -q -b 1 -n extras
%apply_patches
%setup -q -b 0 -n %{packdname}
cp -p %{SOURCE2} Makefile
cp -p %{SOURCE3} adb/Makefile
cp -p %{SOURCE4} fastboot/Makefile
cp -p %{SOURCE5} 51-android.rules

%build
for i in $(find . -name Makefile);do sed -i 's!$(TOOLCHAIN)gcc!%{__cc}!g' $i;done
export CC=%{__cc}
%make CC=%{__cc} CFLAGS="%{optflags}" LDFLAGS="%{ldflags}"

%install
install -d -m 0755 %{buildroot}%{_bindir}
install -d -m 0775 %{buildroot}%{_sharedstatedir}/adb
make install DESTDIR=$RPM_BUILD_ROOT BINDIR=%{_bindir}
install -p -D -m 0644 %{SOURCE6} \
    %{buildroot}%{_unitdir}/adb.service

%post
%systemd_post adb.service

%preun
%systemd_preun adb.service

%postun
%systemd_postun_with_restart adb.service

%files
%doc adb/OVERVIEW.TXT adb/SERVICES.TXT adb/NOTICE adb/protocol.txt 51-android.rules
%{_unitdir}/adb.service
%attr(0755,root,root) %dir %{_sharedstatedir}/adb
#ASL2.0
%{_bindir}/adb
#ASL2.0 and BSD.
%{_bindir}/fastboot
