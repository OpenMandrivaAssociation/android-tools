#!/bin/sh
VERSION="$1"
[ -z "$VERSION" ] && VERSION=`cat *.spec |grep '^Version: ' |awk '{ print $2; }'`
git clone --single-branch --depth 1 -b android-$VERSION https://android.googlesource.com/platform/system/core.git
git clone --single-branch --depth 1 -b android-$VERSION https://android.googlesource.com/platform/system/extras.git
git clone --single-branch --depth 1 -b android-$VERSION https://android.googlesource.com/platform/external/e2fsprogs.git
git clone --single-branch --depth 1 -b master https://github.com/ggrandou/abootimg.git
cd core
git archive -o ../core-${VERSION}.tar --prefix platform/system/core/ android-$VERSION
cd ../extras
git archive -o ../extras-${VERSION}.tar --prefix platform/system/extras/ android-$VERSION
cd ../e2fsprogs
git archive -o ../e2fsprogs-${VERSION}.tar --prefix platform/external/e2fsprogs/ android-$VERSION
cd ../abootimg
git archive -o ../abootimg-$(date +%Y%m%d).tar --prefix abootimg/ origin/master
cd ..
xz -9ef *.tar
