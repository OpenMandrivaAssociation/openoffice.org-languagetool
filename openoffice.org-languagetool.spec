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

%define version	3.0.1
%define rel	0.9.7.1

%define unopkgname	LanguageTool-0.9.7.oxt

Summary:	Rule-based language checker for English, German, Polish, Dutch and other languages.
Name:		%name
Version:	%version
Release:	%mkrel %rel
License:	GPL
Group:		Office
URL:            http://www.languagetool.org/
# tarball created from: 
# cvs -z3 -d:pserver:anonymous@languagetool.cvs.sourceforge.net:/cvsroot/languagetool co -r V_0_9_7 -P JLanguageTool
Source:         languagetool-0.9.7.tar.bz2
Patch0: 	ooo-jars-path.patch
BuildRoot:	%{_tmppath}/%{name}-root
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
can be written in Java. You can think of LanguageTool as a tool to detect errors 
that a simple spell checker cannot detect, e.g. mixing up there/their, no/now etc. 
It can also detect some grammar mistakes. It does not include spell checking.

# %ifarch x86_64
# %package -n %binname
# Summary:        Finnish spellchecker and hyphenator for OpenOffice.org
# Group:		Office
# Requires:       locales-fi
# # Binaries are hidden inside a zip, so automatic dependencies won't work
#Requires:       %{mklibname voikko 1}
# Requires:       voikko-dictionary
# Requires:       %ooname-common = %ooo_version
# Requires(pre):  %ooname-common = %ooo_version
# Requires(post): %ooname-common = %ooo_version
# Requires(preun):        %ooname-common = %ooo_version

# %description -n %binname

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
# openoffice.org upgrade for safe it's reinstalling the extension 
idlangtool=$(%unopkg list --shared 2> /dev/null | sed -ne 's/^Identifier: \(org.openoffice.languagetool.oxt.*\)/\1/p');
%unopkg remove --shared $idlangtool 2> /dev/null
%unopkg list --shared &> /dev/null
%unopkg add --shared %{_libdir}/%{ooodir}/%{unopkgname} 2> /dev/null
%unopkg list --shared &> /dev/null


# (anssi) Map of triggercity:
# Note that installation of voikko implies automatic uninstallation of old
# versions for the compatible instance of openoffice.org.
# Upgrade of openoffice.org-voikko:
# - TRIGGERUN of old version is run, but $1 = 1 and $2 = 1, thus no action is
#   taken
# - POSTTRANS of new version installs new version
# Upgrade of openoffice.org to a compatible version:
# - TRIGGERUN is run, but $1 = 1 and $2 = 1, thus no action is taken
# Upgrade of openoffice.org and openoffice.org-voikko to a compatible version:
# - TRIGGERUN of old version is run, but $1 = 1 and $2 = 1, thus no action is
#   taken
# - TRIGGERUN of old version is run again, but $1 = 1 and $2 = 1, thus no
#   action is taken
# - POSTTRANS of new version installs new version
# Upgrade of openoffice.org and openoffice.org-voikko to an incompatible
# version:
# - TRIGGERIN of old version removes old version
# - TRIGGERUN of old version is run, but $1 = 1 and $2 = 1, thus no action is
#   taken
# - openoffice.org files are replaced with new versions
# - POSTTRANS of new version installs new version
# Upgrade of openoffice.org to an incompatible version, with
# openoffice.org-voikko being removed:
# - TRIGGERIN removes voikko
# - TRIGGERUN is run, but $1 = 1 and $2 = 1, thus no action is taken
# - openoffice.org files are replaced with new versions
# Downgrade of openoffice.org-voikko:
# - TRIGGERUN of new version is run, but $1 = 1 and $2 = 1, thus no action is
#   taken
# - POSTTRANS of old version installs old version
# Removal of openoffice.org-voikko:
# - TRIGGERUN removes voikko as $1 = 0 and $2 = 1
# Removal of openoffice.org and openoffice.org-voikko
# - TRIGGERUN removes voikko as $1 = 1 and $2 = 0
# - openoffice.org files are removed
#

# Posttrans is used instead of post to allow upgrade from old
# openoffice.org-voikko with preun that would remove the new version installed
# in post, without adding triggers for that.

## %posttrans %binpkg
## if [ -x %unopkg ]; then
##	# unopkg writes into $HOME
##	TMP_HOME=$(mktemp -t -d %{binname}.XXXXXX) || exit 1
##	export HOME=$TMP_HOME
##	# make sure no other version is installed
##	for pkg in $(%unopkg list --shared 2>/dev/null | sed -ne 's/^Identifier: \(org.puimula.ooovoikko\)/\1/p'); do
##		%unopkg remove --shared $pkg
##	# empty line due to macro expansion
##	done
##	%unopkg add --shared %{_libdir}/%{binname}/%{unopkgname}
##	rm -rf $TMP_HOME
## fi

## %triggerun %binpkg -- %ooname-common = %ooo_version
## %triggerun %binpkg -- %ooname-common = %ooo_version
# Preun script cannot be used for this as rpm doesn't honor Requires(preun),
# but just removes OOo before preun would be run.
# Executed just before OOo or voikko is being completely removed. Does not run
# on normal upgrades.
## if [ $1 -eq 0 ] || [ $2 -eq 0 ]; then
##	if [ -x %unopkg ]; then
##		# unopkg writes into $HOME
##		TMP_HOME=$(mktemp -t -d %{binname}.XXXXXX) || exit 1
##		export HOME=$TMP_HOME
##		%unopkg remove --shared org.puimula.ooovoikko
##		# get rid of cache:
##		%unopkg list --shared &>/dev/null
##		rm -rf $TMP_HOME
##	fi
## fi
## true

## %triggerin %binpkg -- %ooname-common > %ooo_version
# Executed just before OOo is being upgraded to an incompatible version.
# Cannot be in preun for the same reason as above triggerun.
## if [ -x %unopkg ]; then
##	# unopkg writes into $HOME
##	TMP_HOME=$(mktemp -t -d %{binname}.XXXXXX) || exit 1
##	export HOME=$TMP_HOME
##	%unopkg remove --shared org.puimula.ooovoikko
##	# get rid of cache:
##	%unopkg list --shared &>/dev/null
##	rm -rf $TMP_HOME
## fi

%files 
%defattr(-,root,root)
%{_libdir}/%{ooodir}/%{unopkgname}

