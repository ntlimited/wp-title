#!/usr/bin/python

# script to copy and rename television episodes

import argparse
import os
import re
import shutil
import sys
import time

import wikipedia
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser(description="Copy and rename television episodes")
parser.add_argument('directory', metavar='directory', type=str, nargs='+', help='Directory or directories containing downloaded episodes. Note that the same flag set is used for each directory given, meaning that if the name or season flags are passed unwanted behavior may result. Passing multiple directories is best used when the name/season are auto-detect friendly and sources/etc are all the same')
parser.add_argument('-n', '--name', dest='name', help='Name of show, used to name the folder that files will be moved under and (by default) for wikipedia lookups', default=None)
parser.add_argument('-s', '--season', dest='season', help='Season number - not used if Anime (-j/--japanese) flag is passed', type=int, default=None)
parser.add_argument('-m', '--move', dest='move', default=False, action='store_const', const=True, help='Move files instead of copying')
parser.add_argument('-f', '--folder', dest='folder', default=None, help='Set subfolder name to use instead of default Season X/Series X. Can be a format string')
parser.add_argument('-t', '--to', dest='to', default=None, help='Set root destination to shift media to')
parser.add_argument('-b', '--british', dest='british', default=False, action='store_const', const=True, help='Use "Series" instead of "Season"')
parser.add_argument('-a', '--autoconfirm', dest='autoconfirm', default=False, action='store_const', const=True, help='Don\'t prompt to confirm operation')
parser.add_argument('-w', '--wikiname', dest='wikiname', default=None, help='Set alternate title to use for Wikipedia search')
parser.add_argument('-j', '--japan', dest='japanese', default=False, action='store_const', const=True, help='Optimize for Anime; changes root folder (overridable via -t/--to flag), does not require a season, and uses settings more amenable to formatting commonly used for Anime titles in Wikipedia')
parser.add_argument('-i', '--ignore', dest='ignore', default=0, type=int, help='Number of episodes in target folder to ignore (usually used for "episode 0", etc). The -I/--ignore-end flag is used to ignore trailer episodes')
parser.add_argument('-I', '--ignore-end', dest='ignore_end', default=0, type=int, help='Number of episodes in target folder to ignore at the end of the season. The -i/--ignore flag is used to ignore episodes at the beginning of the season.')
parser.add_argument('-q', '--quiet', dest='quiet', default=False, action='store_const', const=True, help='Do not print to console')
parser.add_argument('--namefile', dest='namefile', help='Optional name file to use for episode titles instead of accessing wikipedia')
parser.add_argument('--header', dest='header', default=None, help='Set alternate section header to search for on Wikipedia page that has the episode listing')
parser.add_argument('--web', dest='from_web', default=False, action='store_const', const=True, help='Flag to mark episodes as being from a web source, changing the name of the created folder for the season')
parser.add_argument('--tv', dest='from_tv', default=False, action='store_const', const=True, help='Flag to mark episodes as being from a TV source, changing the name of the created folder for the season')
parser.add_argument('--filler', dest='filler', default=None, help='Filler episode numbers to remove')
parser.add_argument('--offset', dest='offset', default=0, type=int, help='Episode number offset (used for combining split seasons) - if an episode collection begins at episode 8, --offset 7 would properly number and title the given episodes')
parser.add_argument('--missing', dest='missing', default=0, type=int, help='Episodes missing from the tail end of the season (used for combining split seasons) - if an episode collection ends with episode 7 but the season is 14 episodes long, --missing 7 will allow the script to account for the "missing" files')
parser.add_argument('--multititle', dest='multititle', default=False, action='store_const', const=True, help='For episodes that have multiple titles on Wikipedia (expressed by multiple sections encapsulated by double quotes on the episode listing), record all, separated by " - ". Can also be useful for anime titles if the both English and Japanese titles are desired.')
#parser.add_argument('--merged', dest='merged', default=None, help='For episodes that are split into multiple files (e.g. "Part 1/2/3") but treated by Wikipedia as a single episode, they can be merged together using the syntax 5:6,10:12, etc. For multi-season jobs, merges for a specific season can be expressed via season.episode:episode, e.g. 5.5:6, 5.10:12, and so on. A series name may also be included, e.g. "The Simpsons.5.5:6"')

guess_regex = (re.compile(r"^([A-Za-z0-9\ '\._-]+)[Ss](\d+)"),
               re.compile(r"^([A-Za-z0-9\ '\._-]+)[Ss]eason.*?(\d+)"),
               re.compile(r"^\[.+\]([A-Za-z0-9\ '\._-]+)[Ss](\d+)"),
               re.compile(r"^\[.+\]([A-Za-z0-9\ '\._-]+)[Ss]eason.*?(\d+)"))

extensions = ('.avi', '.mp4', '.mkv')

is_video = lambda x:reduce(lambda a,b:a or b, [x.endswith(ext) for ext in extensions])

default_location = '/media/media/TV'

class Colorize(object):
    '''
    Bash colorization util. Strings are appended to the buffer
    by calling the colorizer like a function, and the buffer is
    flushed to the console by calling it with no arguments.
    Colors are also callable and will wrap the text they are called
    with appropriately. The "color stack" is maintained, so if
    colors are procedurally added, successive use of the Colorize.end
    color will switch back text to the prior color appropriately.

    It is a good idea to call Colorize.clear() before exiting to
    ensure that the terminal is reset properly.
    '''

    class Color(object):
        def __init__(self, code):
            self._code = code

        def code(self):
            return self._code

        def __call__(self, *args):
            return Colorize.AppliedColor(self, args)

    class AppliedColor(object):
        def __init__(self, color, components):
            self._color = color
            self._components = components

        def apply(self, colorizer):
            colorizer(self._color)
            for comp in self._components:
                colorizer(comp)
            colorizer(Colorize.end)

    class Alias(object):

        def __init__(self, aliases):
            for (alias ,color) in aliases.iteritems():
                assert isinstance(color, Colorize.Color)
                setattr(self, alias, color)

    black = Color('\033[0;30m')
    blue = Color('\033[0;34m')
    cyan = Color('\033[0;36m')
    red = Color('\033[0;31m')
    purple = Color('\033[0;35m')
    brown = Color('\033[0;33m')
    light_gray = Color('\033[0;37m')
    dark_gray = Color('\033[1;30m')
    light_blue = Color('\033[1;34m')
    light_green = Color('\033[1;32m')
    light_cyan = Color('\033[1;36m')
    light_red = Color('\033[1;31m')
    light_purple = Color('\033[1;35m')
    yellow = Color('\033[1;33m')
    white = Color('\033[1;37m')
    
    end = Color('\033[0m')

    def __init__(self, **aliases):
        self._stack = [self.__class__.end]
        self._buffer = u''
        self._quiet = False
        self._enabled = sys.stdout.isatty()

        self.a = self.__class__.Alias(aliases)


    def __call__(self, *args):
        for arg in args:
            if isinstance(arg, self.__class__.Color):
                if arg == self.__class__.end:
                    self._stack.pop()
                    if self._enabled:self.bufferize(self._stack[-1].code())
                else:
                    self._stack.append(arg)
                    if self._enabled:self.bufferize(arg.code())
            elif isinstance(arg, self.__class__.AppliedColor):
                arg.apply(self)
            elif isinstance(arg, basestring):
                self.bufferize(arg)
            else:
                self.bufferize(str(arg))

        if not args:
            self.flush()

        return self

    def bufferize(self, data):
        self._buffer = self._buffer + u''.join([unichr(ord(x)) for x in data])

    def flush(self):
        if not self._quiet:print self._buffer
        self._buffer = u''

    def clear(self):
        self._stack = [self.__class__.end]
        if self._enabled:self.bufferize(self._stack[0].code())
        self.flush()

    def quiet(self):
        self._quiet = True


# initializer a colorizer with aliases. 'user' is
# user data, things supplied by the user. 'remote'
# is remote data, (currently) from wikipedia, and
# 'program' is for data determined or created by
# the script itself. Aliases are accessed through
# the .a attribute.
C = Colorize(user=Colorize.light_green,
             remote=Colorize.purple,
             program=Colorize.cyan)

class EpisodeUnMergeManager(object):
    def __init__(self, merge_params):
        self._filters = {}
        
        for setting in merge_params.split(','):
            self.configure(setting)

    def configure(self, merge_setting):
        filters = merge_setting.split('.')
        episodes = filters[-1].split(':')

        if len(filters) == 1:
            series = None
            season = None
        elif len(filters) == 2:
            series = None
            season = filters[0]
        elif len(filters) == 3:
            series, season = filters[:2]
        else:
            raise Exception('Invalid merged syntax')

        self._filters[(series, season)] = episodes

    def get_unmerger(self, series=None, season=None):
        f = self._filters.get((series, season))
        if not f:
            f = self._filters.get((None, season))
        if not f:
            f = self._filters.get((None, None))

        if not f:
            return EpisodeUnMergerManager.NoOp()
        return EpisodeUnMergerManager.Unmerger(*f)

    class NoOp(object):
        def unmerge(self, episodes):
            return episodes

    class Unmerger(object):
        def __init__(self, start, end):
            pass

def main(name=None,
         season=None,
         namefile=None,
         move=False,
         to=None,
         directory=[],
         british=False,
         autoconfirm=False, 
         from_web=False,
         from_tv=False,
         wikiname=None,
         offset=0,
         missing=0,
         japanese=False,
         ignore=0,
         ignore_end=0,
         quiet=False,
         multititle=False,
         folder=None,
         filler=None,
         header=None):

    if quiet:
        if not autoconfirm:
            raise Exception('Quiet mode cannot be used without autoconfirm (-a)')
        C.quiet()

    if japanese and not to:
        to = '%s/Anime' % (default_location,)
    else:
        to = default_location

    if not name or (not japanese and not season):
        global guess_regex
    
        C('Guessing name from directory (', C.a.user(directory[0]), ') ... ')

        gname = None
        gseason = None

        for pat in guess_regex:
            match = pat.search(directory[0])
            if match:
                gname = match.groups()[0].replace('.', ' ').title()
                gname = gname.replace(' A ', ' a').replace(' To ', ' to ') \
                             .replace(' The ', ' the ').replace(' Is ', ' is ') \
                             .replace(' And ', ' and ').replace(' Of ', ' of ') \
                             .replace(' In ', ' in ').replace("'S", "'s").strip()
                gseason = str(int(match.groups()[1]))
                break

        if not gname:
            raise Exception('unable to autodetect name')
        
        name = name or gname
        season = season or gseason

        C("'", C.a.program(name), '\' (season ', C.a.program(season), ')')()

    if namefile:
        names = rename_with_namefile(directory[0], namefile)
    else:
        names = rename_from_wp(directory[0], wikiname or name, season, header, japanese, multititle)

    if filler:
        filler_episodes = map(int,filler.split(','))
        episodes = []
        for (i,e) in enumerate(names):
            if i not in filler_episodes:
                episodes.append(e)
        names = episodes

    files = get_files(directory[0])

    if len(files)+offset+missing-ignore-ignore_end != len(names):
        if not namefile:
            with open('%s.S%.2d' % (name.replace(' ', '.').replace('\'',''), int(season or 0)), 'wb') as handle:
                for name in names:
                    handle.write(name.encode('UTF-8'))
                    handle.write('\n')
        raise Exception('episode count (%d) != file count (%d)' % (len(names),
                                                                   len(files)))

    ignore_end = len(files) - ignore_end

    for f, n in zip(files[ignore:ignore_end], names[offset:]):
        C(C.a.user(f), ' => ', C.a.remote(n))()

    destination = to

    if folder:
        season_name = folder
        if '%s' in folder:
            season_name = season_name % (season,)
        elif '%d' in folder:
            season_name = season_name % (int(season),)
    elif japanese:
        season_name = '.'
    elif british:
        season_name = u'Series %s' % (season,)
    else:
        season_name = u'Season %s' % (season,)

    # tag source for files to ensure ease in upgrading later
    if from_web:
        season_name += ' (web)'
    elif from_tv:
        season_name += ' (TV)'

    destination = os.path.join(destination.encode('UTF-8'),
                               name.encode('UTF-8'),
                               season_name.encode('UTF-8'))
    C('shifting to ', C.a.user(destination))()

    if not autoconfirm:
        while True:
            opt = raw_input('Confirm copy [Y/n]: ')
            if not opt or opt in 'Yy':
                break
            if opt in 'Nn':
                raise Exception('Operation cancelled')

    try:
        os.makedirs(destination)
    except:
        C('destination already exists, ignoring')()

    for (i, (f, e)) in enumerate(zip(files[ignore:ignore_end], names[offset:])):

        extension = f.split('.')[-1]
        target = os.path.join(destination, u'%.2d - %s.%s' % (i+1+offset,
                                                              u''.join([unichr(ord(x)) for x in e]),#e.encode('UTF-8'),
                                                              extension))
        source = f

        size = os.stat(source).st_size >> 20

        if not move:
            C('\tcopying ', C.a.user(size), ' megabytes to ', C.a.program(target))()
        
            start = time.time()
            shutil.copyfile(source, target)
            elapsed = time.time() - start
            C('\t\tCompleted in ',
              C.a.program('%.2f' % (elapsed,)),
              ' seconds (',
              C.a.program('%.2f' % (size/elapsed,),
              'MB/s',')'))()
        else:
            C('\tmoving ', C.a.user(size>>20), ' megabytes to ', C.a.program(target))()

            shutil.move(source, target)

    C(C.white('done'))()

def fix_name(name, japanese=False, multititle=False):
    '''
    Remove illegal characters that cannot be used in Windows paths
    '''

    if name[0] == '"':
        if not multititle:
            name = name[1:name[1:].index('"')+1]
        else:
            pattern = re.compile('"(.+?)"')
            name = u' - '.join(pattern.findall(name))

    name = re.sub(r'\[\d+\]', '', name)

    return name.replace('\\', '') \
               .replace('<', '') \
               .replace('>', '') \
               .replace(':', ' - ') \
               .replace('/', ' - ') \
               .replace('|', '') \
               .replace('?', '') \
               .replace('*', '') \
               .replace('  ', ' ')

def get_files(directory):
    '''
    Get ordered video files from the source directory
    '''
    found = os.listdir(directory)

    unpacked = []
    for f in found:
        if os.path.isdir(os.path.join(directory, f)):
            sub = os.listdir(os.path.join(directory, f))
            if len(sub) is 1 and is_video(sub[0]) and 'sample' not in f.lower():
                unpacked.append(os.path.join(f, sub[0]))
        else:
            unpacked.append(f)
    found = unpacked

    found = [f for f in found if is_video(f)]
    return sorted([os.path.join(directory, x) for x in found],
                  key=lambda x:str.lower(x).replace(' ', '.'))

def rename_from_wp(directory, name, season, header, japanese, multititle):
    list_names = ('List of %s episodes',
                  'List of %s (TV series) episodes',
                  'List of %s media',
                  '%s (TV series)',
                  '%s')

    found = False
    for pat in list_names:
        search_results = wikipedia.search(pat % (name,))

        if search_results[0] != pat % (name,):
            continue
        
        found = True
        break
    
    if not found:
        raise Exception('couldn\'t find episode list')

    page = wikipedia.page(search_results[0])
    soup = BeautifulSoup(page.html())
 
    if season:
        iseason = int(season)
    else:
        iseason = 0

    found = False

    for h3 in soup.find_all('h3'):
        if 'Season %d' % (iseason) in h3.text:
            found = True
            break
        if 'Series %d' % (iseason) in h3.text:
            found = True
            break

    if not found:
        for h2 in soup.find_all('h2'):
            if 'Season %d' % (iseason) in h2.text:
                found = True
                h3 = h2
                break
            if 'Series %d' % (iseason) in h2.text:
                found = True
                h3 = h2
                break

    if not found and japanese:
        for h2 in soup.find_all('h2'):
            if 'episode' in h2.text.lower() and 'list' in h2.text.lower():
                found = True
                h3 = h2
                break
            if h2.text == 'Episodes':
                found = True
                h3 = h2
                break

    if not found and japanese:
        for h3 in soup.find_all('h3'):
            if 'episode' in h2.text.lower() and 'list' in h2.text.lower():
                found = True
                break
            if h3.text == 'Episodes':
                found = True
                break

    if not found and header:
        for h3 in soup.find_all('h3'):
            if header in h3.text:
                found = True
                break

    if not found and header:
        for h4 in soup.find_all('h4'):
            if header in h4.text:
                found = True
                h3 = h4
                break

    if not found and header:
        for h2 in soup.find_all('h2'):
            if header in h2.text:
                found = True
                h3 = h2
                break

    if not found:
        raise Exception('could not find section for season %d' % iseason)

    tag = h3.next_sibling

    found = False
    while tag and not found:
        while tag and tag.name != 'table':
            tag = tag.next_sibling

        if not tag:
            break

        col = 0
        found = False
        for th in tag.find_all('th'):
            if 'title' in th.text.strip().lower() or 'episode name' in th.text.strip().lower():
                found = True
                break
            col += 1

        if found:break
        tag = tag.next_sibling

    if not found:
        raise Exception('could not find episode list for season %d' % iseason)

    episodes = []
    
    for tr in tag.find_all('tr'):
        if 'vevent' not in tr.attrs.get('class',[]):continue
        if not len(tr.find_all('td')):continue
        title = tr.find_all('td')[col - len(tr.find_all('th'))].text
        episodes.append(fix_name(title, japanese=japanese,multititle=multititle))

    return episodes

def rename_with_namefile(directory, namefile):
    with open(namefile) as handle:
        return [fix_name(x) for x in handle.read().split('\n') if x]

def main():
    args = parser.parse_args()

    if len(args.directory) > 1:
        assert not args.season, 'Cannot use season with multiple directories'
        # assert not args.name, 'Cannot use name with multiple directories'
        assert not args.namefile, 'Cannot use namefile with multiple directories'
    
        dirs = args.directory
        for d in dirs:
            args.directory = [d]
            main(**vars(args))
    else:
        try:
            main(**vars(parser.parse_args()))
        except Exception, e:
            C(C.red, 'Error: %s' % e, C.end)()
            C.clear()
            raise

if __name__ == '__main__':
    main()
