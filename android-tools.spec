%define date 20130123
%define git_commit 98d0789
%define packdname core-%{git_commit}
#last extras ext4_utils  commit without custom libselinux requirement
%define extras_git_commit 4ff85ad
%define extras_packdname extras-%{extras_git_commit}


Name:          android-tools
Version:       %{date}git%{git_commit}
Release:       5
Summary:       Android platform tools(adb, fastboot)

Group:         Development/Other
# The entire source code is ASL 2.0 except fastboot/ which is BSD
License:       ASL 2.0 and (ASL 2.0 and BSD)
URL:           http://developer.android.com/guide/developing/tools/

#  using git archive since upstream hasn't created tarballs. 
#  git archive --format=tar --prefix=%%{packdname}/ %%{git_commit} adb fastboot libzipfile libcutils libmincrypt libsparse mkbootimg include/cutils include/zipfile include/mincrypt | xz  > %%{packdname}.tar.xz
#  https://android.googlesource.com/platform/system/core.git
#  git archive --format=tar --prefix=extras/ %%{extras_git_commit} ext4_utils | xz  > %%{extras_packdname}.tar.xz
#  https://android.googlesource.com/platform/system/extras.git

Source0:       %{packdname}.tar.xz
Source1:       %{extras_packdname}.tar.xz
Source2:       core-Makefile
Source3:       adb-Makefile
Source4:       fastboot-Makefile
Source5:       51-android.rules
Source6:       adb.service

Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires(postun): rpm-helper
BuildRequires: zlib-devel
BuildRequires: openssl-devel

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
%setup -q -b 0 -n %{packdname}
cp -p %{SOURCE2} Makefile
cp -p %{SOURCE3} adb/Makefile
cp -p %{SOURCE4} fastboot/Makefile
#cp -p %{SOURCE5} 51-android.rules

%build
# Avoid libselinux dependency.
sed -e 's: -lselinux::' -i fastboot/Makefile
sed -e '/#include <selinux\/selinux.h>/d' \
        -e 's:#include <selinux/label.h>:struct selabel_handle;:' \
        -i ../extras/ext4_utils/make_ext4fs.h
sed -e '160,174d;434,455d' -i ../extras/ext4_utils/make_ext4fs.c
%make CC=%{__cc}

%install
install -d -m 0755 %{buildroot}%{_bindir}
make install DESTDIR=%{buildroot} BINDIR=%{_bindir}
install -p -D -m 0644 %{SOURCE6} \
    %{buildroot}%{_unitdir}/adb.service

mkdir -p %{buildroot}%{_sysconfdir}/udev/rules.d/
install -p -D -m 0644 %{SOURCE5} %{buildroot}%{_sysconfdir}/udev/rules.d/

%post
%_post_service adb

%preun
%_preun_service adb

%files
%doc adb/OVERVIEW.TXT adb/SERVICES.TXT adb/NOTICE adb/protocol.txt
%{_sysconfdir}/udev/rules.d/51-android.rules
%{_unitdir}/adb.service
#ASL2.0
%{_bindir}/adb
#ASL2.0 and BSD.
%{_bindir}/fastboot
