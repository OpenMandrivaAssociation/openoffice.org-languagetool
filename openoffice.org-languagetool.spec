%define ooname	openoffice.org
%define ooo_version 1:3.0.1
%define ooo_shortver 3.0.1 
%define ooodir	ooo-%{ooo_shortver}
%define unopkg	unopkg%{ooo_shortver}

%ifarch x86_64
%define ooname openoffice.org64
%define ooodir	ooo-%{ooo_shortver}_64
%endif

## %define binname	%{ooname}-languagetool
%define name	%{ooname}-languagetool

%define version	0.9.7
%define rel	1

%define unopkgname	LanguageTool-0.9.7.oxt

Summary:	Rule-based language checker for English, German, Polish, Dutch and other languages
Name:		%name
Version:	%version
Release:	%mkrel %rel
License:	LGPL
Group:		Office
URL:		http://www.languagetool.org/
# tarball created from: 
# cvs -z3 -d:pserver:anonymous@languagetool.cvs.sourceforge.net:/cvsroot/languagetool co -r V_0_9_7 -P JLanguageTool
Source:         languagetool-0.9.7.tar.bz2
Patch0: 	ooo-jars-path.patch
BuildRoot:	%{_tmppath}/%{name}-root
BuildRequires:  java-1.6.0-openjdk-devel
BuildRequires:	%ooname-common = %ooo_version
BuildRequires:	%ooname-java-common = %ooo_version
BuildRequires:	ant
Requires: 	%ooname-java-common = %ooo_version
Requires(post):	%ooname-common = %ooo_version
Requires(post):	%ooname-core = %ooo_version
Requires(preun): %ooname-common = %ooo_version
Requires(preun): %ooname-core = %ooo_version

%description

LanguageTool is an Open Source language checker for English, German, Polish, Dutch, 
and other languages. It is rule-based, which means it will find errors for which a 
rule is defined in its XML configuration files. Rules for more complicated errors 
can be written in Java. 

%prep
%setup -q -n JLanguageTool
%patch0 -p0 

# ooo 3.0.1 path
sed -i 's@^ext\.ooo\.dir = .*$@ext\.ooo\.dir = %{_libdir}/%{ooodir}@' %{_builddir}/JLanguageTool/build.properties

%build
ant 

%install
rm -rf %{buildroot}

install -d -m755 %{buildroot}%{_libdir}/%{ooodir}
install -m644 dist/%{unopkgname} %{buildroot}%{_libdir}/%{ooodir}

%clean
rm -rf %{buildroot}

%post
# upgrade
if [ $1 -ge 2 ];then
        idlangtool=$(%unopkg list --shared 2> /dev/null | sed -ne 's/^Identifier: \(org.openoffice.languagetool.oxt.*\)/\1/p');
        if [ "z$idlangtool" != "z" ]; then
                %unopkg remove --shared $idlangtool 2> /dev/null
                %unopkg list --shared &> /dev/null
        fi
fi
%unopkg add --shared %{_libdir}/%{ooodir}/%{unopkgname} 2> /dev/null
%unopkg list --shared &> /dev/null

#uninstall
%preun
if [ $1 -eq 0 ];then
        idlangtool=$(%unopkg list --shared 2> /dev/null | sed -ne 's/^Identifier: \(org.openoffice.languagetool.oxt.*\)/\1/p');
        if [ "z$idlangtool" != "z" ]; then
                %unopkg remove --shared $idlangtool 2> /dev/null
                #clean footprint cache
                %unopkg list --shared &> /dev/null
        fi
fi

%triggerin -- %ooname-core = %ooo_version
[ $2 -eq 0 ] || exit 0
# openoffice.org upgrade, it's reinstalling the extension for safe
idlangtool=$(%unopkg list --shared 2> /dev/null | sed -ne 's/^Identifier: \(org.openoffice.languagetool.oxt.*\)/\1/p');
%unopkg remove --shared $idlangtool 2> /dev/null
%unopkg list --shared &> /dev/null
%unopkg add --shared %{_libdir}/%{ooodir}/%{unopkgname} 2> /dev/null
%unopkg list --shared &> /dev/null

%files 
%defattr(-,root,root)
%{_libdir}/%{ooodir}/%{unopkgname}

