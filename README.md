## Gigantum CLI

[![PyPI version](https://badge.fury.io/py/gigantum.svg)](https://badge.fury.io/py/gigantum)
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fgigantum%2Fgigantum-cli.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Fgigantum%2Fgigantum-cli?ref=badge_shield)

Simple user-facing command line interface (CLI) for installing and running the
Gigantum application locally

## Introduction

This Python package is provided as a method to install and run the Gigantum
application, locally on your computer. It provides a simple command line
interface to install, update, start, and stop the application.

More detailed install instructions can be found at the Gigantum
[docs site](https://docs.gigantum.com/docs)

If you encounter any issues or have any questions or comments, please join our
 [Spectrum Chat Community](https://spectrum.chat/gigantum).

## Prerequisites

1. **Python**

   This tool requires that you have Python and
   [pip](https://pip.pypa.io/en/stable/installing/) installed on your system.
   It works with Python 3.4 and newer.

2. **Docker**

   Gigantum requires the free Docker Community Edition to be installed to run
   locally on your computer. You do not need to keep Docker running at all
   times, but it must be open before you start the Gigantum application and
   can be closed after you stop the Gigantum application.

   If you don't already have Docker, you can install it directly from the
   Docker [website](https://www.docker.com/community-edition#/download)

   - Windows:
     - Requires Microsoft Windows 10 Professional, Enterprise, or Education
       (64-bit)
     - On most systems, Virtualization must be enabled in the "BIOS" (aka
       UEFI), and Hyper-V must also be enabled. Docker will usually
       set this for you, but is a good first place to look if things
       aren't working.
     - Requires Docker CE Stable: [https://store.docker.com/editions/community/docker-ce-desktop-windows](https://store.docker.com/editions/community/docker-ce-desktop-windows)

   - Mac:
     - Docker for Mac works on OS X El Capitan 10.11 and newer macOS releases: [https://store.docker.com/editions/community/docker-ce-desktop-mac](https://store.docker.com/editions/community/docker-ce-desktop-mac)

   - Ubuntu:
     - (Recommended Method) Install using Docker's "helper" script, which
       will perform all install steps for you (you may inspect the
       get-docker.sh script before running it):

       ```bash
       $ cd ~
       $ curl -fsSL get.docker.com -o get-docker.sh
       $ sudo sh get-docker.sh
       ```
     - **OR** install manually, following the instructions here:
       [https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/](https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/)
       - Typical installations will use the `amd64` option in step 4 of
         "Setup The Repository"
       - You can skip step 3 of install Docker CE
     - Regardless of the install method used above, it is required that you
       add your normal user account to the `docker` user group so that you
       can run Docker commands without elevated privileges. Run the following
       command and then logout and back into your system for changes to take
       effect.

       ```
       $ sudo usermod -aG docker <your username>
       ```

       - Note, Docker provides this warning when doing this, which in most
         cases is not an issue (it is similar to the risks associated with sudo
         access):

         > WARNING: Adding a user to the "docker" group will grant the ability
         > to run containers which can be used to obtain root privileges on
         > the docker host.  Refer to
         > https://docs.docker.com/engine/security/security/#docker-daemon-attack-surface
         > for more information.

3. **(Optional) Adjust Docker Resources**

On Windows or MacOS, you can configure the amount of CPU and RAM allocated to
Docker by clicking on `Preferences > Advanced` from the Docker Menu. Docker
will use up to the amount specified when operating.

    ![preferences](docs/img/resources.png)

## Install the CLI

This package is available for install via `pip`. It runs on Python 3.4+ and
supports Windows, OSX and Linux.

1. (Optional) To isolate this package from your system Python, it is often best
   to create a virtual environment first.  This is not required, but
   recommended if you feel comfortable enough with Python. The Gigantum CLI
   installs a minimal set of Python dependencies, so in general it should be
   safe to just install if preferred.

   Using [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/):

   ```
   $ mkvirtualenv gigantum
   ```

   If you are familiar with conda or prefer to manually manage a virtualenv (or
   venv), these methods will also work.

2. Install Gigantum CLI

   ```
   $ python3 -m pip install -U gigantum
   ```

   **OR** if you are actively developing the CLI, you may wish to install it
   from a checkout of this repository like so:

   ```
   $ git checkout <URL for gigantum-cli>
   $ python3 -m pip install -e gigantum-cli
   ```

   Do NOT use `python setup.py develop`.

## Commands

The Gigantum CLI provides a few simple commands to support installation,
updating, and use. When the `pip` package is installed, the Gigantum CLI is
installed as a globally available script called `gigantum`.

Usage of the CLI then becomes:

```
$ gigantum [-h] [--tag <tag>] action
```

#### Actions

- `install`
  - **Run this command after installing the CLI for the first time.**
  - Depending on your bandwidth, installing for the first time can take a while
    as the Docker Image layers are downloaded.
  - This command installs the Gigantum application Docker Image for the first
    time and configures your working directory.

- `update`
  - This command updates an existing installation to the latest version of the
    application
  - If you have the latest version, nothing happens, so it is safe to run this
    command at any time.
  - When you run `update`, the changelog for the new version is displayed and
    you are asked to confirm the upload before it begins.
  - Optionally, you can use the `--tag` option to install a specific version
    instead of the latest

- `start`
  - This command starts the Gigantum application
  - Once started, the application User Inteface is available at
    [http://localhost:10000](http://localhost:10000)
  - **Once you create your first LabBook, check your Gigantum working directory
    for LabBook to make sure everything is configured properly. See the
    `Gigantum Working Directory` section for more details.**

- `stop`
  - This command currently stops and removes all Gigantum managed Docker
    containers and performs a container prune operation.

- `feedback`
  - This command opens a browser to discussion board where you can report bugs,
    suggestions, desired features, etc.

## Usage

### Gigantum Working Directory

The Gigantum working directory is where all your work is stored on your local
filesystem. You can interact directly with this directory if you'd like, but it
is recommended to use the Gigantum UI as it ensures all activity is properly
recorded.

The Gigantum working directory location changes based on your operating system:

- **Windows**: `C:\Users\<username>\gigantum`
- **OSX**: `/Users/<username>/gigantum`
- **Linux**: `/home/<username>/gigantum`

This directory follows a standard directory structure that organizes content by
user and namespace. A namespace is the "owner" of a Project, and typically the
creator. The working directory is organized as illustrated below:

```
<Gigantum Working Directory>
    |_ <logged in user's username>
        |_ <namespace>
               |_ labbooks
                  |_ <project name>
```

As an example, if the user `sarah` created 1 Project and downloaded 1 Project
from the user `janet` the directory would look like this:

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

To use the Gigantum application you must have a Gigantum user account. When you
run the application for the first time you can register.

Note that you'll get an extra warning about granting the application access to
your account when you sign in for the first time.  This is an extra security
measure that occurs because the app is running on localhost and not a verified
domain. This is expected.

Once you login, your user identity is cached locally. This lets you run the
application when disconnected from the internet and without needing to log in
again. If you logout, you will not be able to use the application again until
you have internet access and can re-authenticate.

### Typical Work Flow

After everything is installed, a typical usage would follow a workflow like
this:

- Start the Docker app if it is not already running
- Open a terminal
- Activate your virtualenv (if setup)

  ```
  $ workon gigantum
  ```
- Start the application

  ```
  $ gigantum start
  ```
- A browser will open to [http://localhost:10000](http://localhost:10000)
- Perform your desired work
- When complete, stop the application

  ```
  $ gigantum stop
  ```
- If desired, quit the Docker app


## Providing Feedback

If you encounter any issues using the Gigantum CLI, submit them to this [GitHub
repository issues page](https://github.com/gigantum/gigantum-cli/issues).

If you encounter any issues or have any feedback while using the the Gigantum
Application, use the `gigantum feedback` command to open the discussion board.

## Contributing

Gigantum uses the [Developer Certificate of Origin](https://developercertificate.org/). 
This is lightweight approach that doesn't require submission and review of a
separate contributor agreement.  Code is signed directly by the developer using
facilities built into git.

Please see [`docs/contributing.md` in the gtm
repository](https://github.com/gigantum/gtm/tree/integration/docs/contributing.md).

## Credits

TODO


## License
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fgigantum%2Fgigantum-cli.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Fgigantum%2Fgigantum-cli?ref=badge_large)
