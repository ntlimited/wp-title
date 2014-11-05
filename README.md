# wp_title Documentation
wp_title is a Python-based script used to rename and re-locate media files
to a heirarchically arranged repository with the appropriate names for episodes.
Data is retrieved from Wikipedia, and numerous command line flags exist to
assist with the sometimes ill-defined "format" of Wikipedia articles.

## What does this do?

Let's say you have Dexter season 2 (you know, the good one) on Blu-Ray and
you ripped it to a folder on your harddrive and you encoded it to MKV, leaving
you with a folder called (for example) Dexter.S02 and inside you have 12 files,
named Dexter.S02E01.mkv through Dexter.S02E12.mkv. This is informative, but
it's kind of lackluster if you want to find a particular episode. With wp-title,
you can automatically name and move the episodes to a location. For example, if
you have a media share with a directory for TV set up at /media/shared/TV, you
can simply use the following command to move and title all those files:

```
wp-title --to /media/shared/TV ./Dexter.S02
```

This will create a directory at /media/shared/TV/Dexter/Season 2/ and
copy the files into it, named things like "01 - It's Alive!.mkv". You can
specify multiple directories at once, assuming that the script can guess
the show name and season number from the directory format.

## Installing wp_title

Currently, wp_title is not in PyPI (the *Py*thon *P*ackage *I*ndex), so
the only way to install it is to manually download it from Github. There are
options, however, when it comes to how you want to install it. wp_title is
packaged via Python's Setuptools, and accordingly has a number of niceties
baked in.

Please see the following sections for various options of installation (if
you're familiar with setuptools then you can probably skip this - these
sections are intended to be helpful to users who have little domain knowledge)

### A note about setuptools

Using setuptools is definitely the easiest way to go. If you're on a Linux
based OS, you should have Python installed already and may already have
setuptools. To test whether you have setuptools, type **pip** into your
console. If it's found, great! Otherwise, you'll need to install it via your
package manager (e.g., **sudo apt-get install python-setuptools**). Once
you have it installed, any of the following in this section will work.

### Installing to a Python virtualenv

Virtual Environments in Python are a way to create an (almost) totally
isolated system for hosting code. Importantly, if you're on a system
where you don't have root access, this will allow you to install things
without needing root (although you also won't install it globally). To
begin with, create a copy of the source, either by downloading a source
archive (_wp_title-0.1.0.tar.gz_, etc) or cloning the git repository. Create
a virtual environment with the command **virtualenv env**, which will
initialize a directory named 'env' in your current working directory.
Enable the environment with the command **source bin/activate**, and then
run the setup.py file (wherever it ended up being) using **python setup.py
install**. Presto! You now have wp_title on your path, and will have it
there until you leave the environment by logging out or using the **deactivate**
command. Make sure to activate the environment whenever you want to run
the script, and to "uninstall" it, just delete the environment and source.

### Installing system-wide

To install the script on your system (so every user can access it, and
so that it's on your default path), just download the source as per the
previous subsection and run **sudo python setup.py install**. This will
install wp_title and its dependencies to your global python site packages,
which _shouldn't_ cause any problems, but weirder things have happened.

### Running from an egg

Outside of installing the script and using**wp_title** you can also
just download and run one of the .egg files. (**./wp_title-0.1.0-py2.7.egg**).
However, this will require you to have the wikipedia package for Python
installed, which is pretty difficult without setuptools!

### Installing on Windows

To install the script on windows, you're going to need to install Python.
Visit Python.org and you should be able to find a setup/MSI to do so -
it is advisable to install Python 2.7.x as the program has not been tested
on Python 3.x. Once you have Python installed, you can install Setuptools and
follow the rest of the instructions normally. That said, you will probably
have to manually specify the location of your config file manually (via
the **--config** flag).

## Configuring wp_title

Once you have wp_title installed (easier than it looks if you just
skimmed the installation guide), there is some configuration work you
will probably want to do. By default, wp_title looks for configuration
in _~/.config/wp-title.conf_. This file is not created by default, but
uses a very simple config format with (presently) just a couple kyes. The settings
in the conf file are purely related to storage, where you want your media
copied to when it is re-titled. The **storage.root** key sets the root
directory for copying files. Here's an example fully configured conf:

```
[storage]
root=/home/unixname/Video/TV
anime=Anime
```

The **storage.root** key defines the base path for all media when copied,
while **storage.anime** defines a special subdirectory within that base
path for holding Anime shows. Leaving the storage.anime setting empty (or,
more appropriately, set to ".") will result in Anime being in the same directory
with all your other TV shows, which may be your preference. You can override
either of these settings via command line flags

## Using wp_title (Command line flags)

wp_title comes with a LOT of command line options, which are unfortunately
needed due to the large number of situation that can arise regarding differences
in how things are listed on wikipedia and how they end up being in downloaded
shows. While **wp-title --help** will print out an explanation for all the flags
available, hopefully this breakdown is more illuminating.

### Basic options (name and season settings)

While wp_title can often guess the name of a show and the season, it's not
unusual to run into collections that don't match a naming scheme it would recognize.
If wp_title is unable to recognize the name or season of a show, you can tell it
explicitly through the -n (_--name_) and -s (_--season_) flags.

### Wikipedia options

Wikipedia, being user edited, has _something_ like a standard for how episode lists
are handled, but again, it's not unusual to come across instances where there's no
resemblence to the usual pattern. In those cases, you should try to find the episode
list yourself on wikipedia, then assist the script by providing it with information
using the following flags:

- **-w**, **--wikiname**: the page name that contains the episode list. Copy the
exact text of the title, not the URL fragment for it.
- **--header**: the header of the section the episode list is under.

### Storage Options

You can override the directory that media will be copied to using these flags.

- **-t** **--to**: set the root directory (otherwise configurable via the
storage.root configuration key in the .conf file)
- **-f**, **--folder**: if you don't want a generic "Season X" folder under
the show's directory, you can give it another title here. Useful for shows
that have actual names for their seasons, like Blackadder.

### Weird Episode Wrangling Options

Sometimes, episodes semi-officially exist and either you or wikipedia won't
have them. "Episode 00" is a common case, as are epilogues that were later
tacked on and may have been kept separate from the source you retrieved your
files from. There are five (count em) different flags to assist in handling
all these scenarios

- **-i**, **--ignore**: the number of files to ignore from the beginning of
the season. If YOU have a file for Episode 00 and wikipedia doesn't recognize
its existence, -i 1 will skip it from being included (and also copied).
- **-I**, **--ignore-end**: the number of files to ignore from the end of
the season. If YOU have a file for some epilogue episode that is not in the
Wikipedia episode list, -I 1 will skip it from being included (and also copied)
- **--offset**: This is used for combining split seasons. If you have a folder
that has episodes 8-16 of a split season, --offset 7 will tell the script to
number your episodes 8-16 and not worry about episodes 1-7
- **--missing**: This is the complement to --offset, used for when you have
the starting half of the season.
- **--filler**: Commonly used for anime, this tells the script "ignore these
episode numbers entirely". For instance, if you have a 25 episode series where
episode 13 is a pointless recap that you don't have, --filler 13 will re-number
the episodes appropriately and copy all 25 of your episodes, numbered 1 through 25.
You can specify multiple episodes by separating them with commas. This is useful
in other ways as well - you can use this also to ignore "part 2" of episodes that
you have as a single file.

### The -j Flag

This flag gets its own section as it has numerous effects. -j, or --japan, is
used for Anime shows and - most importantly - causes the script to ignore the
concept of television seasons. It also changes the root folder to append the
configured anime directory, and makes the Wikipedia scraper look for several
weird header name styles that I've encountered while naming Anime files.

### Namefiles

Sometimes, it's just not possible to reconcile your TV episodes with Wikipedia.
The most common reason is that your files and wikipedia fundamentally disagree
on how multipart episodes are grouped. When this happens, you can use a namefile
(literally just a list of names) to manually tell the script how to name episodes.
The **--namefile** flag lets you specify such a file. Usefully, if the episode
list is found but the script can't reconcile it with your files, a namefile will be
created and stored to show.name.SXX, which you can then manually edit until it fits
with your episodes.

### Miscellaneous Options

These aren't strictly needed for anything, but they're there if you want to
add slightly more nuance to your collection.

- **-b**, **--british**: If the show is from the UK, you can use this flag so
that each season is stored in a folder labelled "Series X" as opposed to
"Season X". This also helps with wikipedia sometimes, as it will similarly tell the script
to look for a header labelled 'Series X'
- **--web**: If the show was procured through a web source (downloaded from Youtube, Hulu,
iTunes, etc), this will add a marker to the season's folder to remind you in case a better
source becomes available.
- **--tv**: Similarly to --web, this is used for shows procurred by recording TV broadcasts
- **--multititle**: Sometimes, TV shows have multiple titles given; for instance,
foreign language shows may have their translated name in english and the original name
as well. Using the multitle option will include all names listed, separated by dashes.
- **-m**, **--move**: Instead of copying files, move them. This is useful if you have
no need to keep the files in their original location anymore.
- **-l**, **--link**: Instead of copying files, create a hard link instead. This is \*nix
only, as Windows does not support hard links.
- **-q**, **--quiet**: Don't print any output and work silently. A classic command line
flag mainly included for nostalgia.
- **-a**, **--autoconfirm**: Don't confirm before moving files. This is slightly dangerous,
but most of the time things work out okay. Not advisable if you're working with shows that
have lots of multipart episodes, filler content, or potentially weird episode reordering.

## Contributing

If you would like to contribute, feel free! I am open to both suggestions for features
and patches. This script started out as a personal project and the code quality shows -
if you want to do some refactoring, by all means. Pinging me through github works, and
if you know my username elsewhere, feel free to PM me.
