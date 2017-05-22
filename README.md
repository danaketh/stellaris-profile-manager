# Stellaris Profile Manager

Profile manager for [Stellaris](http://store.steampowered.com/app/281990/) game to let you switch between different mods with ease.

![Thumbnail of the SPM](screenshot.png)

## Prerequisites
- Python 3.5+

## Installation

Clone the source locally:
```bash
$ git clone https://github.com/danaketh/stellaris-profile-manager.git
$ cd stellaris-profile-manager
```

Install the dependencies:
```bash
$ pip install -r requirements.txt
```
## Run

Just have Python to run the script:
```bash
$ python SPM.py
```

## Build

On Windows that is what we the the PyInstaller for. You'll need to have Python 3.5 installed to do that since 3.6
is not yet supported.

```bash
$ pyinstaller SPM.py --noconsole --onefile --paths <PATH_TO_QT5_DLLS>
```

Then, after the app is built for the first time, you can simply use the spec file to build it:

```bash
$ pyinstaller SPM.spec
```

## Export / Import of profiles

When the app is started, it will check for a directory called `profiles` and if it doesn't exist,
it will try to create it. This is where the exported profiles are stored.

### Export

When you mark a profile and press the `Export` button, a file will be created in `profiles/`,
having the name of the exported profile. Just send it around as you wish. The content of this
file is a simple JSON.

### Import

Just copy the exported profile you've got to the `profiles/` directory. When you press the `Import`
button in the app, you'll be presented with a dialog of available profiles. Click the one you wish
to import and do so. If a profile of such name exists, it will NOT be overwritten. Instead a timestamp
is going to be appended to the name of the newly imported profile. This is to prevent you
from accidentally overwriting your profiles.
