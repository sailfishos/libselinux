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

%define libsepolver 2.7-1
# our old rpm doesn't yet support the rundir macro
%if ! %{defined _rundir}
%define _rundir %{_localstatedir}/run
%endif

%define python3_sitearch /%{_libdir}/python3.?/site-packages

Summary: SELinux library and simple utilities
Name: libselinux
Version: 2.7
Release: 11%{?dist}
License: Public Domain
Group: System Environment/Libraries
# https://github.com/SELinuxProject/selinux/wiki/Releases
Source: %{name}-%{version}.tar.bz2
#Source1: selinuxconlist.8
#Source2: selinuxdefcon.8
Url: https://github.com/SELinuxProject/selinux/wiki
Patch1: ln_old_coreutils.patch
BuildRequires: libsepol-static >= %{libsepolver} swig xz-devel python3-base python3-devel pcre-devel
BuildRequires: systemd
# we don't build python2 modules, but make clean expects python2 (could be patched out though)
BuildRequires: python
Requires: libsepol%{?_isa} >= %{libsepolver}
#Conflicts: filesystem < 3, selinux-policy-base < 3.13.1-138

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
Group: Development/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}

%description utils
The libselinux-utils package contains the utilities

%package -n python3-libselinux
Summary: SELinux python 3 bindings for libselinux
Group: Development/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}
%{?python_provide:%python_provide python3-libselinux}
# Remove before F30
Provides: %{name}-python3 = %{version}-%{release}
Provides: %{name}-python3%{?_isa} = %{version}-%{release}
Obsoletes: %{name}-python3 < %{version}-%{release}

%description -n python3-libselinux
The libselinux-python3 package contains python 3 bindings for developing
SELinux applications. 

%package devel
Summary: Header files and libraries used to build SELinux
Group: Development/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: libsepol-devel%{?_isa} >= %{libsepolver}

%description devel
The libselinux-devel package contains the libraries and header files
needed for developing SELinux applications. 

%package static
Summary: Static libraries used to build SELinux
Group: Development/Libraries
Requires: %{name}-devel%{?_isa} = %{version}-%{release}

%description static
The libselinux-static package contains the static libraries
needed for developing SELinux applications. 

%prep
%setup -q -n %{name}-%{version}/upstream
%patch1

%build
# only build libsepol
cd %{name}
export LDFLAGS="%{?__global_ldflags}"
export DISABLE_RPM="y"
export USE_PCRE2="n"

# To support building the Python wrapper against multiple Python runtimes
# Define a function, for how to perform a "build" of the python wrapper against
# a specific runtime:
BuildPythonWrapper() {
  BinaryName=$1

  # Perform the build from the upstream Makefile:
  make \
    PYTHON=$BinaryName \
    LIBDIR="%{_libdir}" CFLAGS="-g %{optflags}" %{?_smp_mflags} \
    pywrap
}

make clean
make LIBDIR="%{_libdir}" CFLAGS="-g %{optflags}" %{?_smp_mflags} swigify
make LIBDIR="%{_libdir}" CFLAGS="-g %{optflags}" %{?_smp_mflags} all

BuildPythonWrapper %{__python3}

make SHLIBDIR="%{_libdir}" LIBDIR="%{_libdir}" LIBSEPOLA="%{_libdir}/libsepol.a" CFLAGS="-g %{optflags}" %{?_smp_mflags}

%install
InstallPythonWrapper() {
  BinaryName=$1

  make \
    PYTHON=$BinaryName \
    LIBDIR="%{_libdir}" CFLAGS="-g %{optflags}" %{?_smp_mflags} \
    LIBSEPOLA="%{_libdir}/libsepol.a" \
    pywrap

  make \
    PYTHON=$BinaryName \
    DESTDIR="%{buildroot}" LIBDIR="%{buildroot}%{_libdir}" \
    SHLIBDIR="%{buildroot}/%{_lib}" BINDIR="%{buildroot}%{_bindir}" \
    SBINDIR="%{buildroot}%{_sbindir}" \
    LIBSEPOLA="%{_libdir}/libsepol.a" \
    install-pywrap
}

# only install libselinux
cd %{name}
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_tmpfilesdir}
mkdir -p %{buildroot}%{_libdir}
mkdir -p %{buildroot}%{_includedir}
mkdir -p %{buildroot}%{_sbindir}
install -d -m 0755 %{buildroot}%{_rundir}/setrans
echo "d %{_rundir}/setrans 0755 root root" > %{buildroot}%{_tmpfilesdir}/libselinux.conf

InstallPythonWrapper %{__python3}

make DESTDIR="%{buildroot}" LIBDIR="%{buildroot}%{_libdir}" SHLIBDIR="%{buildroot}%{_libdir}" BINDIR="%{buildroot}%{_bindir}" SBINDIR="%{buildroot}%{_sbindir}" install

# Nuke the files we don't want to distribute
rm -f %{buildroot}%{_sbindir}/compute_*
rm -f %{buildroot}%{_sbindir}/deftype
rm -f %{buildroot}%{_sbindir}/execcon
rm -f %{buildroot}%{_sbindir}/getenforcemode
rm -f %{buildroot}%{_sbindir}/getfilecon
rm -f %{buildroot}%{_sbindir}/getpidcon
rm -f %{buildroot}%{_sbindir}/mkdircon
rm -f %{buildroot}%{_sbindir}/policyvers
rm -f %{buildroot}%{_sbindir}/setfilecon
rm -f %{buildroot}%{_sbindir}/selinuxconfig
rm -f %{buildroot}%{_sbindir}/selinuxdisable
rm -f %{buildroot}%{_sbindir}/getseuser
rm -f %{buildroot}%{_sbindir}/togglesebool
rm -f %{buildroot}%{_sbindir}/selinux_check_securetty_context
mv %{buildroot}%{_sbindir}/getdefaultcon %{buildroot}%{_sbindir}/selinuxdefcon
mv %{buildroot}%{_sbindir}/getconlist %{buildroot}%{_sbindir}/selinuxconlist
install -d %{buildroot}%{_mandir}/man8/
#install -m 644 %{SOURCE1} %{buildroot}%{_mandir}/man8/
#install -m 644 %{SOURCE2} %{buildroot}%{_mandir}/man8/
rm -f %{buildroot}%{_mandir}/man8/togglesebool*

#%ldconfig_scriptlets
%post
/sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%doc %{name}/LICENSE
%{_libdir}/libselinux.so.*
%dir %{_rundir}/setrans/
%{_sbindir}/sefcontext_compile
%{_tmpfilesdir}/libselinux.conf

%files utils
%{_sbindir}/avcstat
%{_sbindir}/getenforce
%{_sbindir}/getsebool
%{_sbindir}/matchpathcon
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
%{_mandir}/man5/*
%{_mandir}/man8/*

%files devel
%{_libdir}/libselinux.so
%{_libdir}/pkgconfig/libselinux.pc
%{_includedir}/selinux/
%{_mandir}/man3/*

%files static
%{_libdir}/libselinux.a

%files -n python3-libselinux
%{python3_sitearch}/selinux/
%{python3_sitearch}/_selinux.*.so
