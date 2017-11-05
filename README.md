## Gigantum CLI
Simple user-facing command line interface for installing and running the Gigantum Platform locally

## Introduction
This Python package is provided as a method to install and run the Gigantum Platform, locally on your computer. It provides 
simple command line interface to install, update, start, and stop the application. Currently this is only targeting
alpha testers and not generally available yet.

If you encounter any issues or have any questions do not hesitate in contacting Gigantum for help. 

## Prerequisites

1. **Python**

    This simple tool requires that you have Python installed on your system. It works with Python 2.7 and 3.4+. 
    
2. **Docker**

    Gigantum requires the free Docker Community Edition to be installed to run locally on your computer. If you don't 
    already have Docker, you can install it directly from the Docker [website](https://www.docker.com/community-edition#/download)
    
    - Windows:
        - Requires Microsoft Windows 10 Professional or Enterprise 64-bit. For previous versions get Docker Toolbox.
        - [https://store.docker.com/editions/community/docker-ce-desktop-windows](https://store.docker.com/editions/community/docker-ce-desktop-windows)
    
    - Mac:
        - Docker for Mac works on OS X El Capitan 10.11 and newer macOS releases.
        - [https://store.docker.com/editions/community/docker-ce-desktop-mac](https://store.docker.com/editions/community/docker-ce-desktop-mac)
    
    - Ubuntu:
        - To install manually, follow the instructions here: [https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/](https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/)
            - Typical installations will use the `amd64` option in step 4 of "Setup The Repository"
            - You can skip step 3 of install Docker CE
        - To install using Docker's "helper" script, which will perform all install steps for you:
        
            ```bash
            cd ~
            curl -fsSL get.docker.com -o get-docker.sh
            sudo sh get-docker.sh
            ``` 
        - Regardless of the install method used above, it is required that you add your normal user account to the Docker user group 
        so that you can run Docker commands without elevated privileges. Run the following command and then logout and back 
        into your system for changes to take effect.
            
            ```
            sudo usermod -aG docker <your username>
            ```
            
            - Note, Docker provides this warning when doing this:
            
                ```
                WARNING: Adding a user to the "docker" group will grant the ability to run
                containers which can be used to obtain root privileges on the
                docker host.
                Refer to https://docs.docker.com/engine/security/security/#docker-daemon-attack-surface
                for more information.
                ```
            

## Install the CLI

This package is available for install via `pip`. It runs on Python 2 and 3 and supports Windows, OSX and Linux. Currently,
Windows support is limited to Windows 10 Professional, do to Docker support. 

1. (Recommended, but not required) Create a virtual environment before installing the CLI

	Using [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/):
	
	```
	mkvirtualenv gigantum
	```
		
2. Install Gigantum CLI
	
	```
	workon gigantum
	pip install -U gigantum-cli
	```
    

## Commands

The Gigantum CLI provides a few simple commands to support installation, updating, and use. When the `pip` package is installed
the Gigantum CLI is installed as a globally available script called `gigantum`. Usage of the CLI then becomes:

```
> gigantum [-h] [--tag <tag>] action
```

#### Actions

- `install`
    - **Run this command after installing the CLI for the first time.**
    - Depending on your bandwidth, installing for the first time can take a while as the Docker Image layers are downloaded for the first time.
    - This command installs the Gigantum application Docker Image for the first time and configures your working directory.
    
        The Gigantum working directory changes based on your operating system:
        
        - Windows: C:\\Users\<username>\gigantum
        - OSX: /Users/<username>/gigantum
        - Linux: /home/<username>/gigantum

- `update`
    - This command updates an existing installation to the latest version of the application
    - If you have the latest version, nothing happens, so it is safe to run this command at any time.
    - When you run this command, the changes for the new version are displayed and you are asked to confirm the upload before it begins.

- `start`
    - This command starts the Gigantum application
    - Once running, the UI is available at [http://localhost:10000](http://localhost:10000)
    - Currently, any running Jupyter instance will be available at [http://localhost:8888](http://localhost:8888)
    
- `stop`
    - This command currently stops the Gigantum Application and ALL Docker containers
    
- `feedback`
    - This command opens a browser to a feedback form
    
    
## Providing Feedback

If you encounter any issues using the Gigantum CLI, submit them to this GitHub repository issues page.

If you encounter any issues or have any feedback on the Gigantum Application, use the feedback command to open a feedback form.

For urgent issues, contact Gigantum.