## How to install NZBMegasearch + NGINX + GUNICORN

This document explains how to install NZBMegasearch for handling heavy traffic by combining with nginx and Gunicorn.


It has been heavily tested by large quantity of users in the last months.

Who need this?

* moderate to high traffic websites
* who wants an exact replica of mega.nzbx.co ;)

---

### Content

* STEP 0: Tools needed 
* STEP 1: Installation and configuration
* STEP 2: All systems ready

---

### STEP 0: Tools needed

A linux system. You also need:

* nginx and supervisord: `$ sudo apt-get install nginx supervisor`
* gunicorn: `$ sudo easy_install gunicorn`

---

### STEP 1: Installation and configuration

* Install NZBMegasearch (**not as root**) in `/opt/` (or wherever else) by:  
```
$ cd /opt/
$ git clone https://github.com/pillone
```
> This will produce `/opt/usntssearch/`

* All the example configuration files are with respect to that directory.

* Edit, if needed, and copy the nginx conf file: `$ sudo cp /opt/usntssearch/large_server/nginx.conf /etc/nginx/` 

* Edit the 'user' field in the files contained in: `/opt/usntssearch/large_server/supervisor/conf.d/*.conf`


* Depending on the expected traffic, change the parameter `-w 15` (number of concurrent workers) in `/opt/usntssearch/large_server/supervisor/conf.d/mega2.py`

* Copy the supervisor configuration: `$ sudo cp -r /opt/usntssearch/large_server/supervisor /etc`

* Remove the init.d file `$ sudo rm /etc/init.d/nginx`. Supervisor will take care of running and restarting all the services

---

### STEP 2: All systems ready!

* Generate a valid configuration for  NZBMegasearch:
```
$ cd /opt/usntssearch/NZBmegasearch
$ python mega2.py
``` 
> then visit `http://serveripaddress:5000` and configure it. Alternatively, you can use a `custom_params.ini` that you have already saved from a home install.

* This will start all the services:
```
$ sudo supervisorctl reread
$ sudo supervisorctl update
$ sudo supervisorctl restart all
```

* **THAT'S IT! You have successfully installed NZBMegasearch!**

`



