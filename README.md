# tracking-termites
##### CV tools for the watchful termitologist.


About
===============

_TrackingTermites_ is a set of tools designed to facilitate the tracking of termites
samples in experiments footage video (mostly involving confinement in Petri plates).

We're currently able to track the samples positions, their encounters with other
individuals and the distances between them. Useful image preprocessing filters are
also included.

[![Demo](http://img.youtube.com/vi/oenoPR35KxI/0.jpg)](http://www.youtube.com/watch?v=oenoPR35KxI)

[![Demo](http://img.youtube.com/vi/yKXcV2L-ilY/0.jpg)](http://www.youtube.com/watch?v=yKXcV2L-ilY)

The project is conducted at [University Federal of Viçosa Termitology Lab](https://www.isoptera.ufv.br/).

Code tested on Windows 10 and Ubuntu 16.04, requires Python >= 3.5.X, OpenCV == 3.0.2,
Numpy >= 1.13.1.

Getting started
===============

### Windows

On Windows we recommend that you install Python 3 via the [official website](https://www.python.org/) and
download or clone the source code repository. Them proceed as follow:

* Inside the _trackingtermites/_ folder, locate the requirements.txt and install dependencies by
running:

```
    pip install -r requirements.txt
```

* Edit the _config/tracking.conf_ for configuring video source and trackers parameters.

* You should now be able to track termites by running the tracking.py file:

```
    python tracking.py
```

The output is written at the specified path at the configuration file.

### Ubuntu

Installing OpenCV in Ubuntu is being troublesome lately, for your convenience we provide a script
for installation at a [GitHub Gist](https://gist.github.com/dmrib/b2bc06ed8bcf583686e26af6b06f1675).

The script install the required packages and creates a virtual environment containing an OpenCV
installation, the project repository is cloned at Desktop and can be moved to the path of your
preference afterwards.

To track termites, edit the _config/tracking.conf_ for configuring video source and trackers parameters
and run a session of _tracking.py_:

```
   ./tracking.py
```

Remember to always activate the virtual environment before running the script:

```
   workon trackingtermites
```


License
===============

MIT

Contact
===============

* Danilo Ribeiro - _dmrib.cs@gmail.com_
* Og DeSouza - _isoptero@gmail.com_
