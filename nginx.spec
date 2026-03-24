%global _disable_ld_no_undefined 1

%define nginx_home /var/lib/nginx
%define nginx_home_tmp %{nginx_home}/tmp
%define nginx_logdir /var/log/nginx
%define nginx_confdir %{_sysconfdir}/nginx
%define nginx_modulesdir %{_libdir}/nginx
%define nginx_datadir %{_datadir}/nginx
%define nginx_webroot /srv/www/html

%global optflags %{optflags} -O3

Summary:	Robust, small and high performance HTTP and reverse proxy server
Name:		nginx
Version:	1.29.7
Release:	1
Group:		System/Servers
# BSD License (two clause)
# http://www.freebsd.org/copyright/freebsd-license.html
License:	BSD
Url:		https://nginx.net/
Source0:	http://nginx.org/download/%{name}-%{version}.tar.gz
Source1:	https://github.com/sergey-dryabzhinsky/nginx-rtmp-module/archive/refs/tags/v1.2.2-r1.tar.gz
Source2:	https://github.com/kvspb/nginx-auth-ldap/archive/refs/heads/master.tar.gz#/nginx-auth-ldap-2024.04.24.tar.gz
Source3:	https://github.com/nginx/njs/archive/refs/tags/0.9.6.tar.gz
Source4:	https://github.com/openresty/headers-more-nginx-module/archive/refs/tags/v0.39.tar.gz
Source5:	https://github.com/google/ngx_brotli/archive/refs/heads/master.tar.gz#/ngx-brotli-2023.10.09.tar.gz
Source6:	https://github.com/vozlt/nginx-module-vts/archive/refs/tags/v0.2.5.tar.gz
Source51:	nginx.service
Source52:	nginx.logrotate
Source53:	ssl.conf
Source54:	nginx.conf
Source55:	compression.conf
Source56:	realip.conf
Source57:	default.conf
Source100:	index.html
Source101:	poweredby.png
Source102:	nginx-logo.png
Source103:	50x.html
Source104:	404.html

# Patches   0- 99: for nginx itself
Patch0:		nginx-more-mime-types.patch
# Patches 100-199: for nginx-rtmp-module
# No releases forever, but some activity in git
Patch100:	https://github.com/sergey-dryabzhinsky/nginx-rtmp-module/commit/ca49a08e46f66fd0f117eefcaad711b00ccd7bf8.patch
Patch101:	https://github.com/sergey-dryabzhinsky/nginx-rtmp-module/commit/c1f13b7e0a780bd1b85aacf31cad57bdbc6c2559.patch
Patch102:	https://github.com/sergey-dryabzhinsky/nginx-rtmp-module/commit/5d21f4538153e01ea1424df1f334c816cba94938.patch
Patch103:	https://github.com/sergey-dryabzhinsky/nginx-rtmp-module/commit/f615a9422c15ca785788ce34df6eae272d6909b6.patch
Patch104:	https://github.com/sergey-dryabzhinsky/nginx-rtmp-module/commit/ab050d9968eaaea1181d4c7a4ad8d62ace809851.patch
Patch105:	https://github.com/sergey-dryabzhinsky/nginx-rtmp-module/commit/6bd707044a5b3bfa486740d864c683652868d66c.patch
Patch106:	https://github.com/sergey-dryabzhinsky/nginx-rtmp-module/commit/0bd662e80a52fc50efbe13c757664fca276aec4b.patch
Patch107:	https://github.com/sergey-dryabzhinsky/nginx-rtmp-module/commit/8ae0cdcbdde6267375194470afece76150f7e1f2.patch
# Patches 200-299: for nginx-auth-ldap
# Patches 300-399: for njs
# Patches 400-499: for headers-more
# Patches 500-599: for ngx-brotli
Patch500:	ngx_brotli-system-libs.patch
# Patches 600-699: for VTS

BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	slibtool
BuildRequires:	make
BuildRequires:	gd-devel
BuildRequires:	GeoIP-devel
BuildRequires:	perl-devel
BuildRequires:	perl(ExtUtils::Embed)
BuildRequires:	pkgconfig(libpcre)
BuildRequires:	pkgconfig(libxslt)
BuildRequires:	pkgconfig(openssl)
BuildRequires:	pkgconfig(ldap)
BuildRequires:	pkgconfig(zlib)
BuildRequires:	pkgconfig(libbrotlienc)
BuildRequires:	pkgconfig(libbrotlidec)
BuildRequires:	systemd-macros
# For _create_ssl_certificate macro
BuildRequires:	rpm-helper
Requires(post):	rpm-helper
Requires:	pcre
Requires:	openssl
Provides:	webserver
Requires:	www-user
Requires(pre):	www-user
%systemd_requires

# As of 1.25.0, the quic patches are merged and the separate quic
# branch packages are obsolete.
%rename nginx-quic

%description
Nginx [engine x] is an HTTP(S) server, HTTP(S) reverse proxy and IMAP/POP3
proxy server written by Igor Sysoev.

%prep
# FIXME %%autosetup doesn't work with multiple -a flags
%setup -q -a1 -a2 -a3 -a4 -a5 -a6
%autopatch -p1 -M 99

cd nginx-rtmp-module-*
%autopatch -p1 -m 100 -M 199

cd ../nginx-auth-ldap-*
%autopatch -p1 -m 200 -M 299

cd ../njs-*
%autopatch -p1 -m 300 -M 399

cd ../headers-more-*
%autopatch -p1 -m 400 -M 499

cd ../ngx_brotli-*
%autopatch -p1 -m 500 -M 599
# Use system libs
# Fix the Filter Module
#sed -i 's|$ngx_addon_dir/deps/brotli/c/include|/usr/include|g' filter/config
# Fix the Static Module
#sed -i 's|$ngx_addon_dir/deps/brotli/c/include|/usr/include|g' static/config

# Remove the check that aborts if the submodule directory is missing
#sed -i '/brotli\/c\/include/d' filter/config
#sed -i '/brotli\/c\/include/d' static/config

cd ../nginx-module-vts-*
%autopatch -p1 -m 600 -M 699


%build
%serverbuild_hardened
%set_build_flags

./configure \
	--user=www \
	--group=www \
	--prefix=%{nginx_datadir} \
	--sbin-path=%{_bindir}/nginx \
	--conf-path=%{nginx_confdir}/nginx.conf \
	--error-log-path=%{nginx_logdir}/error.log \
	--http-log-path=%{nginx_logdir}/access.log \
	--http-client-body-temp-path=%{nginx_home_tmp}/client_body \
	--http-proxy-temp-path=%{nginx_home_tmp}/proxy \
	--http-fastcgi-temp-path=%{nginx_home_tmp}/fastcgi \
	--pid-path=/run/nginx/nginx.pid \
	--lock-path=/run/nginx/nginx.lock \
	--modules-path=%{nginx_modulesdir} \
	--add-dynamic-module=nginx-rtmp-module-* \
	--add-dynamic-module=nginx-auth-ldap-* \
	--add-dynamic-module=njs-*/nginx \
	--add-dynamic-module=headers-more-* \
	--add-dynamic-module=nginx-module-vts-* \
	--add-module=ngx_brotli-* \
	--with-file-aio \
	--with-pcre \
	--with-pcre-jit \
	--with-ipv6 \
	--with-http_ssl_module \
	--with-http_v2_module \
	--with-http_v3_module \
	--with-http_slice_module \
	--with-http_realip_module \
	--with-http_addition_module \
	--with-http_gzip_static_module \
	--with-http_stub_status_module \
	--with-http_xslt_module=dynamic \
	--with-http_image_filter_module=dynamic \
	--with-http_geoip_module=dynamic \
	--with-http_sub_module \
	--with-http_dav_module \
	--with-http_flv_module \
	--with-http_mp4_module \
	--with-http_gunzip_module \
	--with-http_random_index_module \
	--with-http_secure_link_module \
	--with-http_degradation_module \
	--with-http_auth_request_module \
	--with-http_perl_module=dynamic \
	--with-mail=dynamic \
	--with-mail_ssl_module \
	--with-stream=dynamic \
	--with-ld-opt="%{build_ldflags} -Wl,-E" # so the perl module finds its symbols

sed -i -e 's|-Wl,--no-undefined||g' objs/Makefile

# this is only passed to perl module being built and only overrides the
# default '-O' flag which anyways lowers optimizations (which we don't
# want)
%make_build OPTIMIZE="-fno-PIE"

%install
%make_install INSTALLDIRS=vendor

find %{buildroot} -type f -name .packlist -exec rm -f {} \;
find %{buildroot} -type f -name perllocal.pod -exec rm -f {} \;
find %{buildroot} -type f -empty -exec rm -f {} \;
find %{buildroot} -type f -exec chmod 0644 {} \;
find %{buildroot} -type f -name '*.so' -exec chmod 0755 {} \;
chmod 0755 %{buildroot}%{_bindir}/nginx

# Get rid of broken upstream config samples
rm -rf %{buildroot}%{nginx_confdir}/conf.d

# And install our own configs...
install -p -D -m 0644 %{S:51} %{buildroot}%{_unitdir}/nginx.service
install -p -D -m 0644 %{S:52} %{buildroot}%{_sysconfdir}/logrotate.d/nginx
install -p -d -m 0755 %{buildroot}%{nginx_confdir}/conf.d
install -p -m 0644 %{S:53} %{buildroot}%{nginx_confdir}/
install -p -D -m 0644 %{S:54} %{S:55} %{S:56} %{buildroot}%{nginx_confdir}/
install -p -D -m 0644 %{S:54} %{buildroot}%{nginx_confdir}/nginx.conf.default
install -p -d -m 0755 %{buildroot}%{nginx_home_tmp}
install -p -d -m 0755 %{buildroot}%{nginx_logdir}
install -p -d -m 0755 %{buildroot}%{nginx_webroot}
install -p -d -m 0755 %{buildroot}%{nginx_modulesdir}
install -p -d -m 0755 %{buildroot}%{nginx_datadir}/modules
mkdir -p %{buildroot}%{nginx_confdir}/sites-available %{buildroot}%{nginx_confdir}/sites-enabled
install -p -D -m 0644 %{S:57} %{buildroot}%{nginx_confdir}/sites-available/default.conf
ln -s ../sites-available/default.conf %{buildroot}%{nginx_confdir}/sites-enabled/
mkdir -p %{buildroot}%{nginx_confdir}/http.conf.d

install -p -m 0644 %{S:100} %{S:101} %{S:102} %{S:103} %{S:104} %{buildroot}%{nginx_webroot}

# add current version
sed -i -e "s|_VERSION_|%{version}|g" %{buildroot}%{nginx_webroot}/index.html

install -d %{buildroot}%{_mandir}/man8
install -m0644 man/*.8 %{buildroot}%{_mandir}/man8/

for i in 00-stream 01-mail 05-http_perl 10-http_geoip 10-http_xslt_filter 15-http_image_filter 20-rtmp 20-http_auth_ldap 25-http_headers_more_filter 30-http_js 31-stream_js 35-http_vhost_traffic_status; do
	SERVICE="${i:3}"
	PACKAGE="mod-${SERVICE//_/-}"
	echo "load_module \"%{nginx_modulesdir}/ngx_${SERVICE}_module.so\";" >%{buildroot}%{nginx_datadir}/modules/$i.conf
	cat >%{specpartsdir}/$SERVICE.specpart <<EOF
%%%%package $PACKAGE
Summary:	${SERVICE} module for NGINX
Group:		Servers
Requires:	%{name} = %{EVRD}
EOF

	if [[ "${SERVICE}" == "rtmp" || "${SERVICE}" == "stream_js" ]]; then
		echo "Requires:	%{name}-mod-stream = %{EVRD}" >>%{specpartsdir}/$SERVICE.specpart
	fi

	cat >>%{specpartsdir}/$SERVICE.specpart <<EOF
%%%%description $PACKAGE
${SERVICE} module for NGINX

%%%%files $PACKAGE
%{nginx_modulesdir}/ngx_${SERVICE}_module.so
%{nginx_datadir}/modules/$i.conf
EOF

	if [[ "${SERVICE}" == "http_perl" ]]; then
		cat >>%{specpartsdir}/$SERVICE.specpart <<EOF
%%%%dir %{perl_vendorarch}/auto/nginx
%{perl_vendorarch}/nginx.pm
%{perl_vendorarch}/auto/nginx/nginx.so
EOF
	fi

	cat >>%{specpartsdir}/$SERVICE.specpart <<EOF
%%%%post $PACKAGE
if [[ \$1 == 1 ]]; then
	systemctl reload nginx &>/dev/null || :
fi

%%%%postun $PACKAGE
if [[ \$1 == 1 ]]; then
	systemctl reload nginx &>/dev/null || :
fi
EOF
done

install -d %{buildroot}%{_presetdir}
cat > %{buildroot}%{_presetdir}/86-nginx.preset << EOF
enable nginx.service
EOF

%post
%_create_ssl_certificate nginx

%files
%doc LICENSE CHANGES
%dir %{nginx_datadir}
%dir %{nginx_datadir}/modules
%dir %{nginx_modulesdir}
%{_bindir}/nginx
%{_mandir}/man3/nginx.3pm*
%{_mandir}/man8/*
%{_presetdir}/86-nginx.preset
%{_unitdir}/nginx.service
%{nginx_datadir}/html/*.html
/srv/www/html/*.html
/srv/www/html/*.png
%dir %{nginx_confdir}
%dir %{nginx_confdir}/conf.d
%dir %{nginx_confdir}/http.conf.d
%config(noreplace) %{nginx_confdir}/win-utf
%config(noreplace) %{nginx_confdir}/nginx.conf.default
%config(noreplace) %{nginx_confdir}/scgi_params
%config(noreplace) %{nginx_confdir}/scgi_params.default
%config(noreplace) %{nginx_confdir}/fastcgi.conf
%config %{nginx_confdir}/fastcgi.conf.default
%config %{nginx_confdir}/mime.types.default
%config(noreplace) %{nginx_confdir}/fastcgi_params
%config %{nginx_confdir}/fastcgi_params.default
%config(noreplace) %{nginx_confdir}/koi-win
%config(noreplace) %{nginx_confdir}/koi-utf
%config(noreplace) %{nginx_confdir}/nginx.conf
%config(noreplace) %{nginx_confdir}/compression.conf
%config(noreplace) %{nginx_confdir}/realip.conf
%config(noreplace) %{nginx_confdir}/mime.types
%config(noreplace) %{nginx_confdir}/ssl.conf
%dir %{nginx_confdir}/sites-available
%config(noreplace) %{nginx_confdir}/sites-available/default.conf
%dir %{nginx_confdir}/sites-enabled
%config(noreplace) %{nginx_confdir}/sites-enabled/default.conf
%config(noreplace) %{nginx_confdir}/uwsgi_params
%config(noreplace) %{nginx_confdir}/uwsgi_params.default
%config(noreplace) %{_sysconfdir}/logrotate.d/nginx
%attr(-,www,www) %dir %{nginx_home}
%attr(-,www,www) %dir %{nginx_home_tmp}
%attr(-,www,www) %dir %{nginx_logdir}
