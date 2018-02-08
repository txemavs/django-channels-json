# django-channels-json

This is a test project to play with python 2.7, Django 1.11 and Channels v. 1

This setup uses:

* **nginx**: web service, serve static files and redirect to other services.
* **uwsgi**: WSGI service  for HTTP protocol and Django urls 
* **daphne**: ASGI service for Websockets protocol 
* **redis**: A data storage
* **workers**: Django channels

## Overview

The goal is to have three different paths at the web server:
 * /static -> files (web server)
 * /channel -> Websocket connections (ASGI)
 * / -> HTTP requests (WSGI)


## Install

Get all the needed packages:

	sudo apt-get update
	sudo apt-get install nginx python-pip python-dev uwsgi-plugin-python redis-server
	pip install --upgrade pip

### Python enviroment & Django

Create a new python enviroment and install Django

	mkvirtualenv platform
	pip install "django<2"
	django-admin.py startproject platform

Configure the database, STATIC_ROOT and ALLOWED_HOSTS in settings.py and
	
	workon platform
	./manage.py createsuperuser admin
	./manage.py collectstatic

### Configure WSGI 

Install this system wide:
	
	sudo pip install uwsgi

Create /etc/uwsgi/apps-available/platform.ini (symlink to apps-enabled)

	[uwsgi]
		project = platform
		base = /home/user
		chdir = %(base)/%(project)
		home = %(base)/Env/%(project)
		module = %(project).wsgi:application
		master = true
		processes = 5
		logto = %(base)/%(project)/uwsgi.log
		socket = %(base)/%(project)/uwsgi.sock
		chmod-socket = 664
		vacuum = true
		buffer-size = 32768


## Configure ASGI 

Install Django Channels and redis support:

	workon platform
	pip install channels==1.1.8
	pip install asgi_redis

Now we need this 3 services running, see later how to daemonize:

	./manage.py runserver 0.0.0.0:8888
	daphne -b 0.0.0.0 -p 8001 platform.asgi:channel_layer
	./manage.py runworkers
	


## Configure nginx
Example /etc/nginx/

	server {
		listen 80;
		server_name www.platform.example;
		location = /favicon.ico { access_log off; log_not_found off; }
		location /static/ {
			root /home/user/platform;
		}
		location / {
			include uwsgi_params;
			uwsgi_pass unix:/home/txema/otra/info.sock;
		}
		location /channel/ {
			proxy_pass http://127.0.0.1:8001;
			proxy_http_version 1.1;
			proxy_redirect off;
			proxy_set_header Upgrade $http_upgrade;
			proxy_set_header Connection "Upgrade";
			proxy_set_header Host $host;
			proxy_set_header X-Real-IP $remote_addr;
			proxy_set_header X-Fowarded-For $proxy_add_x_forwarded_for;
			proxy_set_header X-Fowarded-Host $server_name;
		}
	}

## Daemonize

### Systemd (Ubuntu 16)
Create this unit files to daemonize all services, Replace "/home/user" and "plafform" as needed.

/etc/systemd/system/uwsgi.service

	[Unit]
		Description=uWSGI Emperor Service
	[Service]
		ExecStartPre=/bin/bash/ -c 'mkdir -p /run/uwsgi; chown user:www-data /run/wsgi'
		ExecStart=/usr/local/bin/uwsgi --emperor /etc/uwsgi/apps-enabled --uid user --gid www-data --logto /home/user/platform/uwsgi.log
		Restart=always
		KillSignal=SIGQUIT
		Type=notify
		NotifyAccess=all
	[Install]
		WantedBy=multi-user.target

Create /etc/systemd/system/daphne.service

	[Unit]
		Description=Daphne ASGI Service
	[Service]
		User = user
		WorkingDirectory=/home/user/platform
		ExecStart=/home/user/Env/platform/bin/daphne -b 127.0.0.1 -p 8001 platform.asgi:channel_layer
		Restart=always
		KillSignal=SIGQUIT
		Type=simple
		NotifyAccess=all
		StandardOutput=syslog
		StandardError=syslog
		SyslogIdentifier=daphne
	[Install]
	WantedBy=multi-user.target

Create /etc/systemd/system/workers.service

	[Unit]
		Description=Django ASGI Workers
	[Service]
		User = user
		WorkingDirectory=/home/user/platform
		ExecStart=/home/user/Env/otra/bin/python /home/user/platform/manage.py runworker
		Restart=always
		KillSignal=SIGQUIT
		Type=simple
		NotifyAccess=all
		StandardOutput=syslog
		StandardError=syslog
		SyslogIdentifier=asgiwrk
	[Install]
		WantedBy=multi-user.target
		

Remember to reload changes:

	systemctl daemon-reload

Manage this services with systemctl stop/start/restart/status commands:

	sudo systemctl start workers


### Upstart (Ubuntu 14)

Create /etc/init/uwsgi.conf

	description "uWSGI application server in Emperor mode"
	start on runlevel [2345]
	stop on runlevel [!2345]
	setuid user
	setgid www-data
	exec /usr/local/bin/uwsgi --emperor /etc/uwsgi/apps-enabled




