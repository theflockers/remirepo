%{!?php_inidir:  %{expand: %%global php_inidir  %{_sysconfdir}/php.d}}
%{!?php_incldir: %{expand: %%global php_incldir %{_includedir}/php}}
%{!?__pecl:      %{expand: %%global __pecl      %{_bindir}/pecl}}

%global pecl_name  json
%global prever     dev
%global with_zts   0%{?__ztsphp:1}

Summary:       Support for JSON serialization
Name:          php-pecl-json
Version:       1.3.0
Release:       0.3%{?dist}
License:       PHP
Group:         Development/Languages
URL:           https://github.com/remicollet/pecl-json-c
# git clone git@github.com:remicollet/pecl-json-c.git
# cd pecl-json-c; pecl package
Source0:       http://pecl.php.net/get/%{pecl_name}-%{version}%{?prever}.tgz

BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-root
BuildRequires: php-devel >= 5.3.0
BuildRequires: php-pear
BuildRequires: pcre-devel
BuildRequires: json-c-devel >= 0.11

Requires(post): %{__pecl}
Requires(postun): %{__pecl}
Requires:      php(zend-abi) = %{php_zend_api}
Requires:      php(api) = %{php_core_api}

Provides:      php-%{pecl_name} = %{version}
Provides:      php-%{pecl_name}%{?_isa} = %{version}
Provides:      php-pecl(%{pecl_name}) = %{version}
Provides:      php-pecl(%{pecl_name})%{?_isa} = %{version}
Conflicts:     php-Json

# Other third party repo stuff
Obsoletes:     php53-pecl-%{pecl_name}
Obsoletes:     php53u-pecl-%{pecl_name}
%if "%{php_version}" > "5.4"
Obsoletes:     php54-pecl-%{pecl_name}
%endif
%if "%{php_version}" > "5.5"
Obsoletes:     php55-pecl-%{pecl_name}
%endif


# Filter private shared
%{?filter_provides_in: %filter_provides_in %{_libdir}/.*\.so$}
%{?filter_setup}


%description
The php-Json module will add support for JSON (JavaScript Object Notation)
serialization to PHP.

This is a dropin alternative to standard PHP JSON extension which
use the json-c library parser.


%package devel
Summary:       JSON developer files (header)
Group:         Development/Libraries
Requires:      %{name}%{?_isa} = %{version}-%{release}
Requires:      php-devel%{?_isa}

%description devel
These are the files needed to compile programs using JSON serializer.


%prep
%setup -q -c 
cd %{pecl_name}-%{version}%{?prever}

# Sanity check, really often broken
extver=$(sed -n '/#define PHP_JSON_VERSION/{s/.* "//;s/".*$//;p}' php_json.h )
if test "x${extver}" != "x%{version}%{?prever:-%{prever}}"; then
   : Error: Upstream extension version is ${extver}, expecting %{version}%{?prever:-%{prever}}.
   exit 1
fi
cd ..

cat > %{pecl_name}.ini << 'EOF'
; Enable %{pecl_name} extension module
extension = %{pecl_name}-c.so
EOF

%if %{with_zts}
# duplicate for ZTS build
cp -pr %{pecl_name}-%{version}%{?prever}  %{pecl_name}-zts
%endif


%build
cd %{pecl_name}-%{version}%{?prever}
%{_bindir}/phpize
%configure \
  --with-libjson \
  --with-php-config=%{_bindir}/php-config
make %{?_smp_mflags}

%if %{with_zts}
cd ../%{pecl_name}-zts
%{_bindir}/zts-phpize
%configure \
  --with-libjson \
  --with-php-config=%{_bindir}/zts-php-config
make %{?_smp_mflags}
%endif


%install
rm -rf %{buildroot}
# Install the NTS stuff
make -C %{pecl_name}-%{version}%{?prever} \
     install INSTALL_ROOT=%{buildroot}
install -D -m 644 %{pecl_name}.ini %{buildroot}%{php_inidir}/%{pecl_name}-c.ini

# Hack to avoid some conflict (debuginfo)
mv %{buildroot}%{php_extdir}/%{pecl_name}.so \
   %{buildroot}%{php_extdir}/%{pecl_name}-c.so \

# Install the ZTS stuff
%if %{with_zts}
make -C %{pecl_name}-zts \
     install INSTALL_ROOT=%{buildroot}
install -D -m 644 %{pecl_name}.ini %{buildroot}%{php_ztsinidir}/%{pecl_name}-c.ini

mv %{buildroot}%{php_ztsextdir}/%{pecl_name}.so \
   %{buildroot}%{php_ztsextdir}/%{pecl_name}-c.so \
%endif

# Install the package XML file
install -D -m 644 package.xml %{buildroot}%{pecl_xmldir}/%{name}.xml


%check
cd %{pecl_name}-%{version}%{?prever}

TEST_PHP_EXECUTABLE=%{_bindir}/php \
TEST_PHP_ARGS="-n -d extension_dir=$PWD/modules -d extension=%{pecl_name}.so" \
NO_INTERACTION=1 \
REPORT_EXIT_STATUS=1 \
%{_bindir}/php -n run-tests.php

%if %{with_zts}
cd ../%{pecl_name}-zts

TEST_PHP_EXECUTABLE=%{__ztsphp} \
TEST_PHP_ARGS="-n -d extension_dir=$PWD/modules -d extension=%{pecl_name}.so" \
NO_INTERACTION=1 \
REPORT_EXIT_STATUS=1 \
%{__ztsphp} -n run-tests.php
%endif


%post
%{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :


%postun
if [ $1 -eq 0 ] ; then
    %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%doc %{pecl_name}-%{version}%{?prever}/{LICENSE,CREDITS,README.md}

%config(noreplace) %{php_inidir}/%{pecl_name}-c.ini
%{php_extdir}/%{pecl_name}-c.so
%{pecl_xmldir}/%{name}.xml

%if %{with_zts}
%{php_ztsextdir}/%{pecl_name}-c.so
%config(noreplace) %{php_ztsinidir}/%{pecl_name}-c.ini
%endif


%files devel
%defattr(-,root,root,-)
%{php_incldir}/ext/json

%if %{with_zts}
%{php_ztsincldir}/ext/json
%endif


%changelog
* Mon Apr 29 2013 Remi Collet <rcollet@redhat.com> - 1.3.0-0.3
- rebuild with latest changes
- use system json-c library
- temporarily rename to jsonc-c.so

* Sat Apr 27 2013 Remi Collet <rcollet@redhat.com> - 1.3.0-0.2
- rebuild with latest changes

* Sat Apr 27 2013 Remi Collet <rcollet@redhat.com> - 1.3.0-0.1
- initial package
