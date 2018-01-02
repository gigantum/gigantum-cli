## Gigantum CLI 
[![PyPI version](https://badge.fury.io/py/gigantum.svg)](https://badge.fury.io/py/gigantum)

Simple user-facing command line interface (CLI) for installing and running the Gigantum application locally

## Introduction
This Python package is provided as a method to install and run the Gigantum application, locally on your computer. It provides a
simple command line interface to install, update, start, and stop the application. 

**Currently this is package only targeting alpha testers and not generally available yet. You must be granted access to the Gigantum Docker Image to install locally**

If you encounter any issues or have any questions, do not hesitate in contacting Gigantum for help. 

## Prerequisites

1. **Python**

    This tool requires that you have Python installed on your system. It works with Python 2.7 and 3.4+. 
    
2. **Docker**

    Gigantum requires the free Docker Community Edition to be installed to run locally on your computer. You do not need
    to keep Docker running at all times, but it must be open before you start the Gigantum application and can be closed
    after you stop the Gigantum application.    
    
    If you don't already have Docker, you can install it directly from the 
    Docker [website](https://www.docker.com/community-edition#/download)
    
    - Windows:
        - **NOTE: Windows is only partially supported. Additional testing is still required due to recent changes with Docker on Windows**
        - Requires Microsoft Windows 10 Professional or Enterprise 64-bit
        - Requires Docker CE Stable
        - [https://store.docker.com/editions/community/docker-ce-desktop-windows](https://store.docker.com/editions/community/docker-ce-desktop-windows)
    
    - Mac:
        - Docker for Mac works on OS X El Capitan 10.11 and newer macOS releases.
        - [https://store.docker.com/editions/community/docker-ce-desktop-mac](https://store.docker.com/editions/community/docker-ce-desktop-mac)
    
    - Ubuntu:
        - (Recommended Method) Install using Docker's "helper" script, which will perform all install steps for you:
        
            ```bash
            cd ~
            curl -fsSL get.docker.com -o get-docker.sh
            sudo sh get-docker.sh
            ``` 
        - **OR** install manually, following the instructions here: [https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/](https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/)
            - Typical installations will use the `amd64` option in step 4 of "Setup The Repository"
            - You can skip step 3 of install Docker CE
        - Regardless of the install method used above, it is required that you add your normal user account to the Docker user group 
        so that you can run Docker commands without elevated privileges. Run the following command and then logout and back 
        into your system for changes to take effect.
            
            ```
            sudo usermod -aG docker <your username>
            ```
            
            - Note, Docker provides this warning when doing this, which in most cases is not an issue:
            
                ```
                WARNING: Adding a user to the "docker" group will grant the ability to run
                containers which can be used to obtain root privileges on the
                docker host.
                Refer to https://docs.docker.com/engine/security/security/#docker-daemon-attack-surface
                for more information.
                ```
    
3. **Sign-In to DockerHub**

    Since the Gigantum application is still a closed alpha, you must be granted access to the Docker image. To do so, 
    first create a free DockerHub account at [https://hub.docker.com/](https://hub.docker.com/) and **send your username to Gigantum**.
    
    - Start your Docker application. 
    - Open the Docker menu by clicking on the app icon in your system tray or taskbar. 
    - Click on Sign-In in the Docker menu, and enter your DockerHub credentials.
    
    ![sign in](docs/img/docker-signin.png)
    
3. **(Optional) Adjust Docker Resources**
	
	You can configure the amount of CPU and RAM allocated to Docker by clicking on `Preferences > Advanced` from the Docker Menu. Docker will use *up to* the amount specified when operating. 

	![preferences](docs/img/resources.png)
           
## Install the CLI

This package is available for install via `pip`. It runs on Python 2 and 3 and supports Windows, OSX and Linux. 

1. To isolate this package from your system Python, it is often best to create a virtual environment first.
This is not required, but recommended if you feel comfortable enough with Python. The Gigantum CLI installs a minimal set of 
Python dependencies, so in general it should be safe to simply install if preferred.

	Using [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/):
	
	```
	mkvirtualenv gigantum
	```
		
2. Install Gigantum CLI
	
	```
	workon gigantum
	pip install -U gigantum
	```
    

## Commands

The Gigantum CLI provides a few simple commands to support installation, updating, and use. When the `pip` package is installed,
the Gigantum CLI is installed as a globally available script called `gigantum`. 

Usage of the CLI then becomes:

```
> gigantum [-h] [--tag <tag>] action
```

#### Actions

- `install`
    - **Run this command after installing the CLI for the first time.**
    - Depending on your bandwidth, installing for the first time can take a while as the Docker Image layers are downloaded.
    - This command installs the Gigantum application Docker Image for the first time and configures your working directory.

- `update`
    - This command updates an existing installation to the latest version of the application
    - If you have the latest version, nothing happens, so it is safe to run this command at any time.
    - When you run `update`, the changelog for the new version is displayed and you are asked to confirm the upload before it begins.
    - Optionally, you can use the `--tag` option to install a specific version instead of the latest

- `start`
    - This command starts the Gigantum application
    - Once started, the application User Inteface is available at [http://localhost:10000](http://localhost:10000)
    - Currently, any running Jupyter instance will be available at [http://localhost:8888](http://localhost:8888) once launched
    - **Once you create your first LabBook, check your Gigantum working directory for LabBook to make sure everything is configured properly. See the `Gigantum Working Directory` section for more details.**
    
- `stop`
    - This command currently stops the Gigantum Application and *ALL* Docker containers on your computer
    
- `feedback`
    - This command opens a browser to a feedback form where you can report bugs, suggestions, desired features, etc.
    
## Usage

### Gigantum Working Directory

The Gigantum working directory is where all your work is stored on your local filesystem. You can interact directly
with this directory if you'd like, but it is recommended to use the Gigantum UI as it ensures all activity is properly
recorded.

The Gigantum working directory location changes based on your operating system:
        
- **Windows**: `C:\\Users\<username>\gigantum`
- **OSX**: `/Users/<username>/gigantum`
- **Linux**: `/home/<username>/gigantum`
    
This directory follows a standard directory structure that organizes content by user and namespace. A namespace is the 
"owner" of a LabBook, and typically the creator. The working directory is organized as illustrated below:

```
<Gigantum Working Directory>
	|_ <logged in user's username>
		|_ <namespace>
   			|_ labbooks
      			|_ <labbook name>
```

As an example, if the user `sarah` created 1 LabBook and downloaded 1 LabBook from the user `janet` the directory would look like this:

```
<Gigantum Working Directory>
	|_ sarah
		|_ sarah
   			|_ labbooks
      			|_ my-first-labbook
		|_ janet
   			|_ labbooks
      			|_ initial-analysis-1
```
        
        
### User Account
To use the Gigantum application you must have a Gigantum user account. When you run the application for the first time you can register. 

Note that you'll get an extra warning about granting the application access to your account when you sign in for the first time. This is an extra security measure that occurs because the app is running on localhost and not a verified domain. This is expected.

Once you login, your user identity is cached locally. This lets you run the application when disconnected from the internet and without logging in again. If you logout, you will not be able to use the application again until you have internet access and can re-authenticate.

### Typical Work Flow

After everything is installed, a typical usage would follow a workflow like this:

- Start the Docker app if it is not already running
- Open a terminal
- Activate your virtualenv (if setup)
	
	```
	workon gigantum
	```
- Start the application

	```
	gigantum start
	```
- A browser will open to [http://localhost:10000](http://localhost:10000)
- Perform your desired work
- When complete, stop the application

	```
	gigantum stop
	```
- If desired, quit the Docker app



### Sharing 

There are two ways to share LabBooks; export/import and remote repository-based sharing. 

### Export/Import
To export a LabBook, click on the the Export button in the LabBook Overview page.

This will download a `.lbk` archive file to the `export` directory in your Gigantum working directory. 
You can then share this file with someone else or archive it.

To import, simply drag-and-drop the `.lbk` file into the Import area in the LabBook Overview page. 

Note that if the file is large, import can take a little while. Also, importing a LabBook detaches it from the source,
so it will always import into the currently logged in user's namespace.

You cannot duplicate LabBooks. If you want to import a LabBook "on top" of an existing LabBook, currently you'll 
have to rename the original LabBook before Import.

### Sharing via remote repository
Currently, only sharing to the Gigantum cloud is supported.

To share via a remote repository, simply click the "publish" button in the LabBook action menu, located in the top right
corner of an opened LabBook. Once published, you'll receive a link that you can share with other users.

By default all LabBooks are private. Click on the `collaborators` button in the LabBook action menu. Enter the Gigantum
username of any users you wish to collaborate with. They can then enter the link returned by the publish operation into
the new LabBook wizard to download and open your LabBook.
    

## Providing Feedback

If you encounter any issues using the Gigantum CLI, submit them to this [GitHub repository issues page](https://github.com/gigantum/gigantum-cli/issues).

If you encounter any issues or have any feedback while using the the Gigantum Application, use the `gigantum feedback` command to open the feedback form.

For urgent issues, contact Gigantum.