# based on work by The Fedora Project (2017)
# Copyright (c) 1998, 1999, 2000 Thai Open Source Software Center Ltd
# 
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

%define libsepolver 3.1

%if ! %{defined python3_sitearch}
%define python3_sitearch /%{_libdir}/python3.?/site-packages
%endif

Summary: SELinux library and simple utilities
Name: libselinux
Version: 3.1
Release: 1
License: Public Domain
URL: https://github.com/SELinuxProject/selinux/wiki
# https://github.com/SELinuxProject/selinux/wiki/Releases
Source: %{name}-%{version}.tar.bz2
Patch0001: 0001-libselinux-Add-build-option-to-disable-X11-backend.patch
Patch0002: 0002-Fix-selinux-man-page-to-refer-seinfo-and-sesearch-to.patch
Patch0003: 0003-libselinux-LABEL_BACKEND_ANDROID-add-option-to-enabl.patch
BuildRequires: libsepol-static >= %{libsepolver}
BuildRequires: pcre-devel
BuildRequires: python3-base
BuildRequires: python3-devel
BuildRequires: systemd
BuildRequires: swig
BuildRequires: xz-devel
Requires: libsepol >= %{libsepolver}

%description
Security-enhanced Linux is a feature of the Linux® kernel and a number
of utilities with enhanced security functionality designed to add
mandatory access controls to Linux.  The Security-enhanced Linux
kernel contains new architectural components originally developed to
improve the security of the Flask operating system. These
architectural components provide general support for the enforcement
of many kinds of mandatory access control policies, including those
based on the concepts of Type Enforcement®, Role-based Access
Control, and Multi-level Security.

libselinux provides an API for SELinux applications to get and set
process and file security contexts and to obtain security policy
decisions.  Required for any applications that use the SELinux API.

%package utils
Summary: SELinux libselinux utilies
Requires: %{name} = %{version}-%{release}

%description utils
The libselinux-utils package contains the utilities

%package utils-extra
Summary: SELinux libselinux extra utilies
Requires: %{name} = %{version}-%{release}

%description utils-extra
The libselinux-utils-extra package contains the extra utilities

%package -n python3-libselinux
Summary: SELinux python 3 bindings for libselinux
Requires: %{name} = %{version}-%{release}
Provides: %{name}-python3 = %{version}-%{release}
Provides: %{name}-python3 = %{version}-%{release}

%description -n python3-libselinux
The libselinux-python3 package contains python 3 bindings for developing
SELinux applications. 

%package devel
Summary: Header files and libraries used to build SELinux
Requires: %{name} = %{version}-%{release}
Requires: libsepol-devel >= %{libsepolver}

%description devel
The libselinux-devel package contains the libraries and header files
needed for developing SELinux applications. 

%package static
Summary: Static libraries used to build SELinux
Requires: %{name}-devel = %{version}-%{release}

%description static
The libselinux-static package contains the static libraries
needed for developing SELinux applications. 

%global shared_make_flags LABEL_BACKEND_ANDROID=y \\\
        DISABLE_X11\=y \\\
        LIBDIR\="%{_libdir}" \\\
        BINDIR\="%{_bindir}" \\\
        SHLIBDIR\="%{_libdir}" \\\
        SBINDIR\="%{_sbindir}"

%prep
%autosetup -p1 -n %{name}-%{version}/upstream

%build
# only build libsepol
cd %{name}
export DISABLE_RPM="y"
export USE_PCRE2="n"

# To support building the Python wrapper against multiple Python runtimes
# Define a function, for how to perform a "build" of the python wrapper against
# a specific runtime:
BuildPythonWrapper() {
  BinaryName=$1

  # Perform the build from the upstream Makefile:
  %make_build \
      PYTHON=$BinaryName \
      %{shared_make_flags} \
      pywrap
}
for target in swigify all ; do
    %make_build $target \
                %{shared_make_flags} \
                CFLAGS="$CFLAGS -fno-semantic-interposition"
done
BuildPythonWrapper %{__python3}

%install
InstallPythonWrapper() {
  BinaryName=$1

  make \
    PYTHON=$BinaryName \
    DESTDIR="%{buildroot}" \
    %{shared_make_flags} \
    LIBSEPOLA="%{_libdir}/libsepol.a" \
    install-pywrap
}
cd %{name}
mkdir -p %{buildroot}%{_tmpfilesdir}
mkdir -p %{buildroot}%{_libdir}
mkdir -p %{buildroot}%{_includedir}
mkdir -p %{buildroot}%{_sbindir}
install -d -m 0755 %{buildroot}%{_rundir}/setrans
echo "d %{_rundir}/setrans 0755 root root" > %{buildroot}%{_tmpfilesdir}/libselinux.conf

InstallPythonWrapper %{__python3}

%{__make} install DESTDIR=%{?buildroot} INSTALL="%{__install} -p" %{shared_make_flags}

mv %{buildroot}%{_sbindir}/getdefaultcon %{buildroot}%{_sbindir}/selinuxdefcon
mv %{buildroot}%{_sbindir}/getconlist %{buildroot}%{_sbindir}/selinuxconlist

#%ldconfig_scriptlets
%post
/sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%license %{name}/LICENSE
%{_libdir}/libselinux.so.*
%dir %{_rundir}/setrans/
%{_tmpfilesdir}/libselinux.conf

%files utils
%defattr(-,root,root,-)
%{_sbindir}/avcstat
%{_sbindir}/getenforce
%{_sbindir}/getsebool
%{_sbindir}/matchpathcon
%{_sbindir}/sefcontext_compile
%{_sbindir}/selinuxconlist
%{_sbindir}/selinuxdefcon
%{_sbindir}/selinuxexeccon
%{_sbindir}/selinuxenabled
%{_sbindir}/setenforce
%{_sbindir}/selabel_digest
%{_sbindir}/selabel_lookup
%{_sbindir}/selabel_lookup_best_match
%{_sbindir}/selabel_partial_match
%{_sbindir}/selinux_check_access
%{_sbindir}/selabel_get_digests_all_partial_matches
%{_sbindir}/validatetrans

%files utils-extra
%defattr(-,root,root,-)
%{_sbindir}/compute_*
%{_sbindir}/getfilecon
%{_sbindir}/getpidcon
%{_sbindir}/policyvers
%{_sbindir}/setfilecon
%{_sbindir}/getseuser
%{_sbindir}/togglesebool
%{_sbindir}/selinux_check_securetty_context

%files devel
%defattr(-,root,root,-)
%{_libdir}/libselinux.so
%{_libdir}/pkgconfig/libselinux.pc
%{_includedir}/selinux/
%{_mandir}/man3/*
%{_mandir}/man5/*
%{_mandir}/man8/*
%{_mandir}/ru/man5/*
%{_mandir}/ru/man8/*

%files static
%defattr(-,root,root,-)
%{_libdir}/libselinux.a

%files -n python3-libselinux
%defattr(-,root,root,-)
%{python3_sitearch}/selinux/
%{python3_sitearch}/selinux-*
%{python3_sitearch}/_selinux*
