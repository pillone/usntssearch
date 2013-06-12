## How to install NZBMegasearch for free on the cloud 

This document explains how to install NZBMegasearch on a freely available free cloud service.
For this task, we will use OpenShift, a cloud computing platform from Red Hat.

It is really very easy to install it by using the step-by-step instructions.

These are the advantages of a cloud-installed NZBMegasearch: 


* it is always online, no need to start it from your computer
* it is connected on a crazy fast network (less waiting time)
* it is free
* your configuration, your providers!
* it is SSL and password protected

Note: This kind of installation does not support heavy traffic/load. It is designed only for personal usage (or small groups).

---

### Content

* STEP 0: Tools needed 
* STEP 1: Register on Openshift
* STEP 2: Create your site on Openshift
* STEP 3: Install NZBMegasearch on the cloud
* STEP ??: Update NZBMegasearch (when updates are available :] )

---

### STEP 0: Tools needed

You only need to install:

* [Git and Rhc: step-by-step install  (Linux, Win, Mac)](https://www.openshift.com/developers/rhc-client-tools-install)
* a [SSH client](http://www.chiark.greenend.org.uk/~sgtatham/putty/) in case you are using Windows (Linux and Mac have it already installed by default)

---

### STEP 1: Register on Openshift

A valid email is required:

* *Register on Openshift*: [https://www.openshift.com/](https://www.openshift.com/)


---

### STEP 2: Create your site on Openshift 

* Go to console, make a folder, enter in it and type:
> `$ rhc app create flask python-2.7`  
> This will take few minutes. The tool will ask for a 'namespace', part of the domain name of your online install. E.g.: If you enter 'dog'. Your url on the cloud will be: `flask-dog.rhcloud.com`

* Continue on the console:
> ```
$ cd flask 
$ git remote add upstream -m master git://github.com/openshift/flask-example.git
$ git pull -s recursive -X theirs upstream master
$ git push
```

* You can now check out that everything has been correctly installed by opening with your browser:
> `http://flask-dog.rhcloud.com/`

---

### STEP 3: Install NZBMegasearch on the cloud

* Login in  [https://www.openshift.com/](https://www.openshift.com/)

* You will be presented with a list of installed applications. Click on 'Flask'. It should also visualize the domain you have created at STEP 3.

* On the page of the Flask application click on the link: `WANT TO LOG IN TO YOUR APPLICATION?`  

* Copy the line similar to this: `ssh 123456890123456890@flask-dog.rhcloud.com`.

* Issue the command:
> `$ ssh 12361287362187368713621@flask-dog.rhcloud.com` (if you are using Windows, put that as your url)

* If everything went fine, you are now logged in the Openshift cloud and you should be presented this kind of prompt:
> `[flask-dog.rhcloud.com 123456890123456890]\>`

* On the remote server prompt (shortened for visibility), type:
> ```
[flask-dog.rhcloud.com]\> cd app-root/repo/wsgi/
[flask-dog.rhcloud.com]\> git clone https://github.com/pillone/usntssearch.git
[flask-dog.rhcloud.com]\> cd usntssearch/NZBmegasearch/openshift
[flask-dog.rhcloud.com]\> ./install_openshift.sh
[flask-dog.rhcloud.com]\> ctl_app restart
```
then select 1 (python-2.7) to start 

* You can now check out that everything has been correctly installed by visiting:
> `http://flask-dog.rhcloud.com/`

* **The DEFAULT username and password are:**
> User: 'NZBMadmin'  
> Pwd: 'NZBMadmin'
> **... that I strongly suggest to change ;)**

* Configure all your options, as a standard NZBMegasearch install

* Disconnect from SSH and remove your directory `flask` on your hard drive

* **THAT'S IT! You have successfully installed NZBMegasearch on the cloud!**

---

### STEP ??: Update NZBMegasearch

* In case updates are available (via notification in NZBMegasearch), you need to:
> Log in: `ssh 12361287362187368713621@flask-dog.rhcloud.com` (if you are using Windows, put that as your url)

* and on the remote prompt:
>``` 
[flask-dog.rhcloud.com]\> cd app-root/repo/wsgi/usntssearch/NZBmegasearch/openshift
[flask-dog.rhcloud.com]\> ./install_openshift.sh
[flask-dog.rhcloud.com]\> ctl_app restart
```
then select 1 (python-2.7) to start 

* You can now disconnect from SSH

* **THAT'S IT! You have successfully updated NZBMegasearch!**


