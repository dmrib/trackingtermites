# tracking-termites
##### CV tools for the watchful termitologist.


About
===============

These are tools that helps biologists extract data from experiments videos of termites under
confinement (mostly in petri dishes).

We're currently able to track the samples positions, compute velocities, distances and detect
encounters between individuals. Encounters can be further classified automatically as actual
interactions or not.

[![Demo](https://img.youtube.com/vi/1OERWG7F74c/0.jpg)](https://www.youtube.com/watch?v=1OERWG7F74c)

[![Demo](https://img.youtube.com/vi/BcPc1BXg5vc/0.jpg)](https://www.youtube.com/watch?v=BcPc1BXg5vcY)

The project is conducted at [Federal University of Viçosa Termitology Lab](https://www.isoptera.ufv.br/).

Code tested on Ubuntu 16.04, requires Python >= 3.6.X.

Getting started
===============

### Windows

On Windows we recommend that you install Python 3.6 via the [official website](https://www.python.org/) and
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

Installing OpenCV in Ubuntu is being troublesome lately. For your convenience we provide a script
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

Funding
===============

FAPEMIG (Fundação de Amparo à Pesquisa do Estado de Minas Gerais)

License
===============

MIT

Contact
===============

* Danilo Ribeiro - _dmrib.cs@gmail.com_
* Og DeSouza - _isoptero@gmail.com_
