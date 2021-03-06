%{!?pear_metadir: %global pear_metadir %{pear_phpdir}}
%{!?__pear: %{expand: %%global __pear %{_bindir}/pear}}
%global pear_name    Horde_Role
%global pear_channel pear.horde.org

Name:           php-horde-Horde-Role
Version:        1.0.1
Release:        1%{?dist}
Summary:        PEAR installer role used to install Horde components

Group:          Development/Libraries
License:        LGPLv2
URL:            http://pear.horde.org
Source0:        http://%{pear_channel}/get/%{pear_name}-%{version}.tgz

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
BuildRequires:  php-pear(PEAR) >= 1.7.0
BuildRequires:  php-channel(%{pear_channel})

Requires(post): %{__pear}
Requires(postun): %{__pear}
Requires:       php-common >= 5.3.0
Requires:       php-pear(PEAR) >= 1.7.0
Requires:       php-channel(%{pear_channel})

Provides:       php-pear(%{pear_channel}/%{pear_name}) = %{version}


%description
This package provides a method for PEAR to install Horde components into
the base Horde installation.

System default Horde installation directory is %{_datadir}/horde.


%prep
%setup -q -c

cat <<EOF | tee macros.horde
# Horde web files location
%%pear_hordedir %%(%%{__pear} config-get horde_dir 2> /dev/null || echo undefined)
EOF

cd %{pear_name}-%{version}

# no PEAR postinstall task. do it in RPM post scriplet.
sed -e '/tasks:/d' \
    ../package.xml >%{name}.xml


%build
cd %{pear_name}-%{version}
# Empty build section, most likely nothing required.


%install
# Horde web files location
mkdir -p %{buildroot}%{_datadir}/horde

# Install new RPM macro
mkdir -p %{buildroot}%{_sysconfdir}/rpm
install -pm 644 macros.horde %{buildroot}%{_sysconfdir}/rpm

cd %{pear_name}-%{version}
%{__pear} install --nodeps --packagingroot %{buildroot} %{name}.xml

# Clean up unnecessary files
rm -rf %{buildroot}%{pear_metadir}/.??*

# Install XML package description
mkdir -p %{buildroot}%{pear_xmldir}
install -pm 644 %{name}.xml %{buildroot}%{pear_xmldir}


%post
%{__pear} install --nodeps --soft --force --register-only \
    %{pear_xmldir}/%{name}.xml >/dev/null || :

%{__pear} config-set \
    horde_dir %{_datadir}/horde \
    system >/dev/null || :

%postun
if [ $1 -eq 0 ] ; then
    %{__pear} uninstall --nodeps --ignore-errors --register-only \
        %{pear_channel}/%{pear_name} >/dev/null || :
fi


%files
%defattr(-,root,root,-)
%doc %{pear_docdir}/%{pear_name}
%{_sysconfdir}/rpm/macros.horde
%{pear_xmldir}/%{name}.xml
%{pear_phpdir}/PEAR/Installer/Role/Horde
%{pear_phpdir}/PEAR/Installer/Role/Horde.php
%{pear_phpdir}/PEAR/Installer/Role/Horde.xml
# Empty dir, used by horde apps.
%dir %{_datadir}/horde


%changelog
* Mon Nov 19 2012 Remi Collet <remi@fedoraproject.org> - 1.0.1-1
- Update to 1.0.1 for remi repo
- License is LGPLv2

* Wed Nov  7 2012 Remi Collet <remi@fedoraproject.org> - 1.0.0-3
- fix xml (install fails because of tasks:postinstallscript)

* Mon Nov  5 2012 Remi Collet <remi@fedoraproject.org> - 1.0.0-2
- cleanups

* Sun Nov  4 2012 Remi Collet <remi@fedoraproject.org> - 1.0.0-1
- Initial package
