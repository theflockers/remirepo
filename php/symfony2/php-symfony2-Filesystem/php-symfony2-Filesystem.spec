%{!?__pear: %{expand: %%global __pear %{_bindir}/pear}}

%global pear_channel pear.symfony.com
%global pear_name    Filesystem
%global php_min_ver  5.3.3

Name:             php-symfony2-%{pear_name}
Version:          2.2.1
Release:          1%{?dist}
Summary:          Symfony2 %{pear_name} Component

Group:            Development/Libraries
License:          MIT
URL:              http://symfony.com/doc/current/components/filesystem.html
Source0:          http://%{pear_channel}/get/%{pear_name}-%{version}.tgz

BuildRoot:        %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:        noarch

BuildRequires:    php-pear(PEAR)
BuildRequires:    php-channel(%{pear_channel})
# For tests
BuildRequires:    php(language) >= %{php_min_ver}
BuildRequires:    php-pear(pear.phpunit.de/PHPUnit)
# For tests: phpci
BuildRequires:    php-ctype
BuildRequires:    php-date
BuildRequires:    php-posix
BuildRequires:    php-spl

Requires:         php(language) >= %{php_min_ver}
Requires:         php-pear(PEAR)
Requires:         php-channel(%{pear_channel})
Requires(post):   %{__pear}
Requires(postun): %{__pear}
# phpci
Requires:         php-ctype
Requires:         php-date
Requires:         php-posix
Requires:         php-spl

Provides:         php-pear(%{pear_channel}/%{pear_name}) = %{version}

%description
The Filesystem component provides basic utilities for the filesystem.


%prep
%setup -q -c

# Create PHPUnit autoloader
( cat <<'PHPUNIT_AUTOLOADER'
<?php

# This file was created by RPM packaging and is not part of the original
# Symfony2 %{pear_name} PEAR package.

set_include_path(
    '%{pear_phpdir}'.PATH_SEPARATOR.
    '%{pear_testdir}/%{pear_name}'.PATH_SEPARATOR.
    get_include_path()
);

spl_autoload_register(function ($class) {
    if ('\\' == $class[0]) {
        $class = substr($class, 1);
    }

    $file = str_replace('\\', '/', $class).'.php';
    @include $file;
});
PHPUNIT_AUTOLOADER
) > phpunit.autoloader.php

# Update PHPUnit config
sed -e 's#vendor/autoload.php#./phpunit.autoloader.php#' \
    -i %{pear_name}-%{version}/Symfony/Component/%{pear_name}/phpunit.xml.dist

# Modify PEAR package.xml file:
# - Remove .gitattributes file
# - Remove .gitignore file
# - Change role from "php" to "doc" for CHANGELOG.md file
# - Change role from "php" to "test" for all test files
# - Remove md5sum from phpunit.xml.dist file since it was updated
sed -e '/\.gitattributes/d' \
    -e '/\.gitignore/d' \
    -e '/CHANGELOG.md/s/role="php"/role="doc"/' \
    -e '/Tests/s/role="php"/role="test"/' \
    -e '/phpunit.xml.dist/s/role="php"/role="test"/' \
    -e '/phpunit.xml.dist/s/md5sum="[^"]*"\s*//' \
    -i package.xml

# package.xml is version 2.0
mv package.xml %{pear_name}-%{version}/%{name}.xml


%build
# Empty build section, nothing required


%install
cd %{pear_name}-%{version}

# PEAR install
%{__pear} install --nodeps --packagingroot %{buildroot} %{name}.xml

# Clean up unnecessary files
rm -rf %{buildroot}%{pear_metadir}/.??*

# Install XML package description
mkdir -p %{buildroot}%{pear_xmldir}
install -pm 644 %{name}.xml %{buildroot}%{pear_xmldir}

# Install PHPUnit autoloader
install -pm 0644 ../phpunit.autoloader.php \
    %{buildroot}/%{pear_testdir}/%{pear_name}/Symfony/Component/%{pear_name}/


%check
cd %{pear_name}-%{version}/Symfony/Component/%{pear_name}

sed 's#./phpunit.autoloader.php#./autoloader.php#' -i phpunit.xml.dist

%{_bindir}/phpunit -d date.timezone="UTC"


%post
%{__pear} install --nodeps --soft --force --register-only \
    %{pear_xmldir}/%{name}.xml >/dev/null || :


%postun
if [ $1 -eq 0 ] ; then
    %{__pear} uninstall --nodeps --ignore-errors --register-only \
        %{pear_channel}/%{pear_name} >/dev/null || :
fi


%files
%defattr(-,root,root,-)
%doc %{pear_docdir}/%{pear_name}
%{pear_xmldir}/%{name}.xml
%dir %{pear_phpdir}/Symfony
%dir %{pear_phpdir}/Symfony/Component
     %{pear_phpdir}/Symfony/Component/%{pear_name}
%{pear_testdir}/%{pear_name}


%changelog
* Sat Apr 06 2013 Remi Collet <remi@fedoraproject.org> - 2.2.1-1
- Update to 2.2.1 (no change)

* Wed Mar 13 2013 Shawn Iwinski <shawn.iwinski@gmail.com> 2.2.0-1
- Updated to 2.2.0
- Removed tests' bootstrap patch

* Tue Mar 05 2013 Remi Collet <remi@fedoraproject.org> - 2.2.0-1
- Update to 2.2.0

* Wed Feb 27 2013 Remi Collet <remi@fedoraproject.org> - 2.1.8-1
- Update to 2.1.8

* Mon Jan 21 2013 Remi Collet <RPMS@FamilleCollet.com> 2.1.7-1
- update to 2.1.7 (no code change)

* Fri Dec 21 2012 Remi Collet <RPMS@FamilleCollet.com> 2.1.6-1
- update to 2.1.6 (no change)

* Fri Dec 21 2012 Remi Collet <RPMS@FamilleCollet.com> 2.1.5-1
- update to 2.1.5

* Thu Nov 29 2012 Remi Collet <RPMS@FamilleCollet.com> 2.1.4-1
- update to 2.1.4

* Tue Nov 13 2012 Shawn Iwinski <shawn.iwinski@gmail.com> 2.1.3-2
- Removed .gitattributes and .gitignore files from package.xml

* Sun Nov 11 2012 Shawn Iwinski <shawn.iwinski@gmail.com> 2.1.3-1
- Updated to upstream version 2.1.3

* Tue Oct 30 2012 Remi Collet <RPMS@FamilleCollet.com> 2.1.3-1
- sync with rawhide, update to 2.1.3

* Mon Oct 29 2012 Shawn Iwinski <shawn.iwinski@gmail.com> 2.1.2-3
- Added "%%global pear_metadir" and usage in %%install
- Changed RPM_BUILD_ROOT to %%{buildroot}
- Changed name of patch from "php-symfony2-Filesystem.tests.bootstrap.patch" to
  "%%{name}-tests-bootstrap.patch"

* Sun Oct  7 2012 Shawn Iwinski <shawn.iwinski@gmail.com> 2.1.2-2
- Added php-posix require
- Added PEAR package.xml modifications
- Added patch for tests' bootstrap.php
- Added tests (%%check)

* Sat Oct  6 2012 Remi Collet <RPMS@FamilleCollet.com> 2.1.2-1
- update to 2.1.2

* Thu Sep 20 2012 Shawn Iwinski <shawn.iwinski@gmail.com> 2.1.2-1
- Initial package
