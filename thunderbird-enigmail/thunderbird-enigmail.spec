%define debug_build       0

# Use system Librairies ?
%if 0%{?fedora} <= 17
%define system_sqlite 0
%else
%define system_sqlite 1
%endif
%if 0%{?fedora} < 15 && 0%{?rhel} < 6
%define system_nspr       0
%define system_nss        0
%else
%define system_nspr       1
%define system_nss        1
%endif
%if 0%{?fedora} < 15
%define system_cairo      0
%define system_vpx        0
%else
%define system_cairo      1
%define system_vpx        1
%endif

%define build_langpacks 1

%define nspr_version 4.9
%define nss_version 3.13.3
%define cairo_version 1.10.0
%define freetype_version 2.1.9
%define lcms_version 1.19
%define sqlite_version 3.7.10
%define libnotify_version 0.4
%global libvpx_version 1.0.0
%define _default_patch_fuzz 2

%define thunderbird_app_id \{3550f703-e582-4d05-9a08-453d09bdfdc6\}

%global thunver  15.0
%global thunmax  16.0

# The tarball is pretty inconsistent with directory structure.
# Sometimes there is a top level directory.  That goes here.
#
# IMPORTANT: If there is no top level directory, this should be 
# set to the cwd, ie: '.'
#%define tarballdir .
%define tarballdir comm-release

%define official_branding 1

%define mozappdir         %{_libdir}/thunderbird
%global enigmail_extname  %{_libdir}/mozilla/extensions/{3550f703-e582-4d05-9a08-453d09bdfdc6}/{847b3a00-7ab1-11d4-8f02-006008948af5}


Summary:        Authentication and encryption extension for Mozilla Thunderbird
Name:           thunderbird-enigmail
Version:        1.4.4
%if 0%{?prever:1}
Release:        0.1.%{prever}%{?dist}
%else
Release:        2%{?dist}
%endif
URL:            http://enigmail.mozdev.org/
License:        MPLv1.1 or GPLv2+
Group:          Applications/Internet
Source0:        thunderbird-%{thunver}%{?thunbeta}.source.tar.bz2
#NoSource:       0

Source10:       thunderbird-mozconfig
Source11:       thunderbird-mozconfig-branded

# ===== Enigmail files =====
%if 0%{?CVS}
# cvs -d :pserver:guest@mozdev.org:/cvs login
# => password is guest 
# cvs -d :pserver:guest@mozdev.org:/cvs co enigmail/src
# tar czf /home/rpmbuild/SOURCES/enigmail-20091121.tgz --exclude CVS -C enigmail/src .
Source100:      enigmail-%{CVS}.tgz
%else
Source100:      http://www.mozilla-enigmail.org/download/source/enigmail-%{version}%{?prever}.tar.gz
%endif


# Mozilla (XULRunner) patches
Patch0:         thunderbird-install-dir.patch
Patch8:         xulrunner-10.0-secondary-ipc.patch

# Build patches
Patch104:       xulrunner-10.0-gcc47.patch

# Linux specific
Patch200:       thunderbird-8.0-enable-addons.patch

# Enigmail patch


%if %{official_branding}
# Required by Mozilla Corporation

%else
# Not yet approved by Mozillla Corporation

%endif

%if %{system_nspr}
BuildRequires:  nspr-devel >= %{nspr_version}
%endif
%if %{system_nss}
BuildRequires:  nss-static
BuildRequires:  nss-devel >= %{nss_version}
%endif
%if %{system_cairo}
# Library requirements (cairo-tee >= 1.10)
BuildRequires:  cairo-devel >= %{cairo_version}
%endif
BuildRequires:  libnotify-devel >= %{libnotify_version}
BuildRequires:  libpng-devel
BuildRequires:  libjpeg-devel
BuildRequires:  zip
BuildRequires:  bzip2-devel
BuildRequires:  zlib-devel, gzip, zip, unzip
BuildRequires:  libIDL-devel
BuildRequires:  gtk2-devel
BuildRequires:  gnome-vfs2-devel
BuildRequires:  libgnome-devel
BuildRequires:  libgnomeui-devel
BuildRequires:  krb5-devel
BuildRequires:  pango-devel
BuildRequires:  freetype-devel >= %{freetype_version}
BuildRequires:  libXt-devel
BuildRequires:  libXrender-devel
BuildRequires:  hunspell-devel
%if %{?system_sqlite}
BuildRequires:  sqlite-devel >= %{sqlite_version}
%endif
BuildRequires:  startup-notification-devel
BuildRequires:  alsa-lib-devel
BuildRequires:  desktop-file-utils
BuildRequires:  libcurl-devel
BuildRequires:  yasm
BuildRequires:  mesa-libGL-devel
BuildRequires:  GConf2-devel
BuildRequires:  lcms-devel >= %{lcms_version}
%if %{system_vpx}
BuildRequires:  libvpx-devel >= %{libvpx_version}
%endif

## For fixing lang
BuildRequires:  perl


# Without this enigmmail will require libxpcom.so and other .so  
# which are not provided by thunderbird (to avoid mistake, 
# because provided by xulrunner). 
AutoReq:  0
# All others deps already required by thunderbird
Requires: gnupg
Requires: thunderbird >= %{thunver}
Requires: thunderbird <  %{thunmax}

# Nothing usefull provided
AutoProv: 0


%description
Enigmail is an extension to the mail client Mozilla Thunderbird
which allows users to access the authentication and encryption
features provided by GnuPG 

#===============================================================================

%prep
%setup -q -c
cd %{tarballdir}

%patch0  -p2 -b .dir
# Mozilla (XULRunner) patches
cd mozilla
%patch8 -p3 -b .secondary-ipc
%patch104 -p1 -b .gcc47
cd ..

%patch200 -p1 -b .addons

%if %{official_branding}
# Required by Mozilla Corporation

%else
# Not yet approved by Mozilla Corporation

%endif


%{__rm} -f .mozconfig
cat %{SOURCE10} 		\
%if ! %{system_nss}
  | grep -v system-nss 		\
%endif
%if ! %{system_nspr}
  | grep -v system-nspr 	\
%endif
%if ! %{system_cairo}
  | grep -v enable-system-cairo    \
%endif
%if ! %{system_vpx}
  | grep -v with-system-libvpx     \
%endif
  | tee .mozconfig

%if 0%{?fedora} < 14 && 0%{?rhel} <= 6
echo "ac_add_options --disable-libjpeg-turbo"  >> .mozconfig
%endif

%if %{official_branding}
%{__cat} %{SOURCE11} >> .mozconfig
%endif

# s390(x) fails to start with jemalloc enabled
%ifarch s390 s390x
echo "ac_add_options --disable-jemalloc" >> .mozconfig
%endif

%if %{?system_sqlite}
echo "ac_add_options --enable-system-sqlite"  >> .mozconfig
%else
echo "ac_add_options --disable-system-sqlite" >> .mozconfig
%endif

%if %{?debug_build}
echo "ac_add_options --enable-debug" >> .mozconfig
echo "ac_add_options --disable-optimize" >> .mozconfig
%else
echo "ac_add_options --disable-debug" >> .mozconfig
echo "ac_add_options --enable-optimize" >> .mozconfig
%endif

%ifarch %{arm}
echo "ac_add_options --disable-elf-hack" >> .mozconfig
%endif

# ===== Enigmail work =====
%if 0%{?CVS}
mkdir mailnews/extensions/enigmail
tar xzf %{SOURCE100} -C mailnews/extensions/enigmail

%else
tar xzf %{SOURCE100} -C mailnews/extensions
pushd mailnews/extensions/enigmail
# From: Patrick Brunschwig <patrick@mozilla-enigmail.org>
# All tarballs (as well as CVS) will *always* report as 1.4a1pre (or whatever
# the next major version would be). This is because I create builds from trunk
# and simply label the result as 1.3.x.
# sed -i -e '/em:version/s/1.5a1pre/%{version}/' package/install.rdf
grep '<em:version>%{version}</em:version>' package/install.rdf || exit 1
# Apply Enigmail patch here
popd
%endif

# ===== Fixing langpack
pushd mailnews/extensions/enigmail
for rep in $(cat lang/current-languages.txt)
do
   perl util/fixlang.pl ui/locale/en-US lang/$rep
done
popd

#===============================================================================

%build
cd %{tarballdir}

# -fpermissive is needed to build with gcc 4.6+ which has become stricter
#
# Mozilla builds with -Wall with exception of a few warnings which show up
# everywhere in the code; so, don't override that.
#
# Disable C++ exceptions since Mozilla code is not exception-safe
#
MOZ_OPT_FLAGS=$(echo "$RPM_OPT_FLAGS -fpermissive" | \
                      %{__sed} -e 's/-Wall//' -e 's/-fexceptions/-fno-exceptions/g')
export CFLAGS=$MOZ_OPT_FLAGS
export CXXFLAGS=$MOZ_OPT_FLAGS

export PREFIX='%{_prefix}'
export LIBDIR='%{_libdir}'

MOZ_SMP_FLAGS=-j1
# On x86 architectures, Mozilla can build up to 4 jobs at once in parallel,
# however builds tend to fail on other arches when building in parallel.
%ifarch %{ix86} x86_64
[ -z "$RPM_BUILD_NCPUS" ] && \
     RPM_BUILD_NCPUS="`/usr/bin/getconf _NPROCESSORS_ONLN`"
[ "$RPM_BUILD_NCPUS" -ge 2 ] && MOZ_SMP_FLAGS=-j2
[ "$RPM_BUILD_NCPUS" -ge 4 ] && MOZ_SMP_FLAGS=-j4
[ "$RPM_BUILD_NCPUS" -ge 8 ] && MOZ_SMP_FLAGS=-j8
%endif


# ===== Thunderbird build =====
# http://enigmail.mozdev.org/download/source.php.html
make -f client.mk build STRIP="/bin/true" MOZ_MAKE_FLAGS="$MOZ_SMP_FLAGS"

# ===== Enigmail work =====
pushd mailnews/extensions/enigmail
./makemake -r
popd

pushd objdir/mailnews/extensions/enigmail
make
make xpi
popd

#===============================================================================

%install
cd %{tarballdir}

mkdir -p $RPM_BUILD_ROOT%{enigmail_extname}
unzip -q objdir/mozilla/dist/bin/enigmail-*-linux-*.xpi -d $RPM_BUILD_ROOT%{enigmail_extname}


%files
%{enigmail_extname}


#===============================================================================

%changelog
* Mon Aug 27 2012 Remi Collet <remi@fedoraproject.org> 1.4.4-2
- Enigmail 1.4.4 for Thunderbird 15.0

* Wed Aug 21 2012 Remi Collet <remi@fedoraproject.org> 1.4.4-1
- Enigmail 1.4.4 for Thunderbird 14.0

* Sat Jul 21 2012 Remi Collet <remi@fedoraproject.org> 1.4.3-1
- Enigmail 1.4.3 for Thunderbird 14.0

* Tue Jun 05 2012 Remi Collet <remi@fedoraproject.org> 1.4.2-1
- Enigmail 1.4.2 for Thunderbird 13.0

* Sat Apr 28 2012 Remi Collet <remi@fedoraproject.org> 1.4.1-1
- Enigmail 1.4.1 for Thunderbird 12.0

* Fri Mar 16 2012 Remi Collet <remi@fedoraproject.org> 1.4-2.1
- latest patch from rawhide

* Thu Mar 15 2012 Remi Collet <remi@fedoraproject.org> 1.4-2
- Enigmail 1.4 for Thunderbird 11.0

* Sat Mar 03 2012 Remi Collet <remi@fedoraproject.org> 1.4-1
- Enigmail 1.4 for Thunderbird 10.0.2
- using upstream fixlang.pl instead of our fixlang.php

* Tue Jan 31 2012 Remi Collet <remi@fedoraproject.org> 1.3.5-1
- Enigmail 1.3.5 for Thunderbird 10.0

* Wed Dec 21 2011 Remi Collet <remi@fedoraproject.org> 1.3.4-1
- Enigmail 1.3.4 for Thunderbird 9.0

* Sat Nov 12 2011 Remi Collet <remi@fedoraproject.org> 1.3.3-1
- Enigmail 1.3.3 for Thunderbird 8.0

* Wed Oct 12 2011 Georgi Georgiev <chutzimir@gmail.com> - 1.3.2-2
- Make it work on RHEL

* Sat Oct 01 2011 Remi Collet <remi@fedoraproject.org> 1.3.2-2
- Enigmail 1.3.2 for Thunderbird 7.0.1
- fix extension version

* Thu Sep 29 2011 Remi Collet <remi@fedoraproject.org> 1.3.2-1
- Enigmail 1.3.2 for Thunderbird 7.0

* Wed Aug 17 2011 Remi Collet <remi@fedoraproject.org> 1.3-1
- Enigmail 1.3 for Thunderbird 6.0

* Sat Jul 30 2011 Remi Collet <remi@fedoraproject.org> 1.2.1-1
- Enigmail 1.2.1 for Thunderbird 5.0

* Tue Jul 19 2011 Remi Collet <remi@fedoraproject.org> 1.2-1.2
- add --enable-chrome-format=jar to generate enigmail.jar

* Sun Jul 17 2011 Remi Collet <remi@fedoraproject.org> 1.2-1.1
- fix BR (dos2unix + php-cli)

* Sun Jul 17 2011 Remi Collet <rpms@famillecollet.com> 1.2-1
- Enigmail 1.2 for Thunderbird 5.0

* Thu Jul 22 2010 Remi Collet <rpms@famillecollet.com> 1.1.2-3
- move to /usr/lib/mozilla/extensions (as lightning)
- build against thunderbird 3.1.1 sources
- sync patches with F-13

* Sat Jul 10 2010 Remi Collet <rpms@famillecollet.com> 1.1.2-2
- remove link mecanism as thundebird dir is now stable (see #608511)

* Wed Jun 30 2010 Remi Collet <rpms@famillecollet.com> 1.1.2-1
- Enigmail 1.1.1 (against thunderbird 3.1)

* Sat Jun 26 2010 Remi Collet <rpms@famillecollet.com> 1.1.1-2
- new sources (only fix displayed version)

* Sat Jun 26 2010 Remi Collet <rpms@famillecollet.com> 1.1.1-1
- Enigmail 1.1.1 (against thunderbird 3.1)

* Mon May 31 2010 Remi Collet <rpms@famillecollet.com> 1.1-1
- Enigmail 1.1 (against thunderbird 3.1rc1)

* Mon Feb 01 2010 Remi Collet <rpms@famillecollet.com> 1.0.1-1
- Enigmail 1.0.1 (against thunderbird 3.0.1)

* Fri Jan 29 2010 Remi Collet <rpms@famillecollet.com> 1.0.1-0.1.rc1
- Enigmail 1.0.1rc1 (against thunderbird 3.0.1)

* Mon Nov 30 2009 Remi Collet <rpms@famillecollet.com> 1.0.0-1
- Enigmail 1.0 (against thunderbird 3.0rc1)

* Sat Nov 21 2009 Remi Collet <rpms@famillecollet.com> 1.0-0.1.cvs20091121
- new CVS snapshot (against thunderbird 3.0rc1)

* Tue Jul 21 2009 Remi Collet <rpms@famillecollet.com> 0.97a-0.1.cvs20090721
- new CVS snapshot (against thunderbird 3.0b3)

* Thu May 21 2009 Remi Collet <rpms@famillecollet.com> 0.96a-0.3.cvs20090521
- new CVS snapshot
- fix License and Sumnary

* Mon May 18 2009 Remi Collet <rpms@famillecollet.com> 0.96a-0.2.cvs20090516
- use mozilla-extension-update.sh from thunderbird-lightning

* Sat May 16 2009 Remi Collet <rpms@famillecollet.com> 0.96a-0.1.cvs20090516
- new CVS snapshot
- rpmfusion review proposal

* Thu Apr 30 2009 Remi Collet <rpms@famillecollet.com> 0.96a-0.1.cvs20090430.fc11.remi
- new CVS snapshot
- F11 build

* Mon Mar 16 2009 Remi Collet <rpms@famillecollet.com> 0.96a-0.1.cvs20090316.fc#.remi
- new CVS snapshot
- add enigmail-fixlang.php

* Sun Mar 15 2009 Remi Collet <rpms@famillecollet.com> 0.96a-0.1.cvs20090315.fc#.remi
- enigmail 0.96a (CVS), Thunderbird 3.0b2

