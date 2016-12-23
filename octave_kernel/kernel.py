from __future__ import print_function

import codecs
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile
from xml.dom import minidom

from metakernel import MetaKernel, ProcessMetaKernel, REPLWrapper, u
from metakernel.pexpect import which
from IPython.display import Image, SVG

from . import __version__


class OctaveKernel(ProcessMetaKernel):
    implementation = 'Octave Kernel'
    implementation_version = __version__,
    language = 'octave'
    language_version = __version__,
    banner = "Octave Kernel",
    language_info = {
        'mimetype': 'text/x-octave',
        'name': 'octave',
        'file_extension': '.m',
        "version": __version__,
        'help_links': MetaKernel.help_links,
    }

    _banner = None
    _octave_engine = None

    @property
    def banner(self):
        if self._banner is None:
            self._banner = self.octave_engine.eval('info', silent=True)
        return self._banner

    @property
    def octave_engine(self):
        if self._octave_engine:
            return self._octave_engine
        self._octave_engine = OctaveEngine(plot_settings=self.plot_settings,
                                           error_handler=self.Error,
                                           stdin_handler=self.raw_input,
                                           stream_handler=self.Print)
        return self._octave_engine

    def makeWrapper(self):
        """Start an Octave process and return a :class:`REPLWrapper` object.
        """
        return self.octave_engine.repl

    def do_execute_direct(self, code, silent=False):
        if code.strip() in ['quit', 'quit()', 'exit', 'exit()']:
            self.do_shutdown(True)
            return
        val = ProcessMetaKernel.do_execute_direct(self, code, silent=silent)
        if not silent:
            plot_dir = self.octave_engine.make_figures()
            for image in self.octave_engine.extract_figures(plot_dir):
                self.Display(image)
            shutil.rmtree(plot_dir, True)
        return val

    def get_kernel_help_on(self, info, level=0, none_on_fail=False):
        obj = info.get('help_obj', '')
        if not obj or len(obj.split()) > 1:
            if none_on_fail:
                return None
            else:
                return ""
        return self.octave_engine.eval('help %s' % obj, silent=True)

    def get_completions(self, info):
        """
        Get completions from kernel based on info dict.
        """
        cmd = 'completion_matches("%s")' % info['obj']
        val = self.octave_engine.eval(cmd, silent=True)
        return val and val.splitlines() or []

    def handle_plot_settings(self):
        """Handle the current plot settings"""
        self.octave_engine.plot_settings = self.plot_settings


class OctaveEngine(object):

    def __init__(self, error_handler=None, stream_handler=None,
                 stdin_handler=None, plot_settings=None):
        self.executable = self._get_executable()
        self.repl = self._create_repl()
        self.error_handler = error_handler
        self.stream_handler = stream_handler
        self.stdin_handler = stdin_handler
        self._startup(plot_settings)

    @property
    def plot_settings(self):
        return self._plot_settings

    @plot_settings.setter
    def plot_settings(self, settings):
        settings = settings or dict(backend='inline')
        self._plot_settings = settings

        # Remove "None" keys so we can use setdefault below.
        keys = ['format', 'backend', 'width', 'height', 'resolution',
                'backend']
        for key in keys:
            if key in settings and settings.get(key, None) is None:
                del settings[key]

        if sys.platform == 'darwin':
            settings.setdefault('format', 'svg')
        else:
            settings.setdefault('format', 'png')

        settings.setdefault('backend', 'inline')
        settings.setdefault('width', -1)
        settings.setdefault('height', -1)
        settings.setdefault('resolution', 0)
        settings.setdefault('name', 'Figure')

        cmds = []
        if settings['backend'] == 'inline':
            cmds.append("set(0, 'defaultfigurevisible', 'off');")
            cmds.append("graphics_toolkit('gnuplot');")
        else:
            cmds.append("set(0, 'defaultfigurevisible', 'on');")
            cmds.append("graphics_toolkit('%s');" % settings['backend'])
        self.eval('\n'.join(cmds))

    def eval(self, code, timeout=None, silent=False):
        """Evaluate code using the engine.
        """
        stream_handler = None if silent else self.stream_handler
        try:
            return self.repl.run_command(code.rstrip(),
                                         timeout=timeout,
                                         stream_handler=stream_handler,
                                         stdin_handler=self.stdin_handler)
        except Exception as e:
            if self.error_handler:
                self.error_handler(e)
            else:
                raise e

    def make_figures(self, plot_dir=None):
        """Create figures for the current figures.

        Parameters
        ----------
        plot_dir: str, optional
            The directory in which to create the plots.

        Returns
        -------
        out: str
            The plot directory containing the files.
        """
        settings = self._plot_settings
        if settings['backend'] != 'inline':
            self.eval('drawnow("expose");')
            if not plot_dir:
                return
        fmt = settings['format']
        res = settings['resolution']
        wid = settings['width']
        hgt = settings['height']
        name = settings['name']
        plot_dir = plot_dir or tempfile.mkdtemp()
        plot_dir = plot_dir.replace(os.path.sep, '/')
        make_figs = '_make_figures("%s", "%s", "%s", %d, %d, %d)'
        make_figs = make_figs % (plot_dir, fmt, name, wid, hgt, res)
        resp = self.eval(make_figs, silent=True)
        if resp and 'error:' in resp:
            if self.error_handler:
                self.error_handler(resp)
            else:
                raise Exception(resp)
        return plot_dir

    def extract_figures(self, plot_dir):
        """Get a list of IPython Image objects for the created figures.

        Parameters
        ----------
        plot_dir: str
            The directory in which to create the plots.
        """
        images = []
        path = os.path.join(plot_dir, '%s*' % self.plot_settings['name'])
        for fname in reversed(glob.glob(path)):
            filename = os.path.join(plot_dir, fname)
            try:
                if fname.lower().endswith('.svg'):
                    im = self._handle_svg(filename)
                else:
                    im = Image(filename)
                images.append(im)
            except Exception as e:
                if self.error_handler:
                    self.error_handler(e)
                else:
                    raise e
        return images

    def _startup(self, plot_settings):
        cwd = os.getcwd().replace(os.path.sep, '/')
        self.eval('more off; source ~/.octaverc; cd("%s");' % cwd)
        here = os.path.realpath(os.path.dirname(__file__))
        self.eval('addpath("%s")' % here.replace(os.path.sep, '/'))
        available = self.eval('available_graphics_toolkits', silent=True)
        if 'gnuplot' not in available:
            msg = ('May not be able to display plots properly '
                   'without gnuplot, please install it')
            if self.error_handler:
                self.error_handler(msg)
            else:
                raise ValueError(msg)
        self.plot_settings = plot_settings

    def _handle_svg(self, filename):
        """
        Handle special considerations for SVG images.
        """
        # Gnuplot can create invalid characters in SVG files.
        with codecs.open(filename, 'r', encoding='utf-8',
                         errors='replace') as fid:
            data = fid.read()
        im = SVG(data=data)
        try:
            im.data = self._fix_svg_size(im.data)
        except Exception:
            pass
        return im

    def _fix_svg_size(self, data):
        """GnuPlot SVGs do not have height/width attributes.  Set
        these to be the same as the viewBox, so that the browser
        scales the image correctly.
        """
        # Minidom does not support parseUnicode, so it must be decoded
        # to accept unicode characters
        parsed = minidom.parseString(data.encode('utf-8'))
        (svg,) = parsed.getElementsByTagName('svg')

        viewbox = svg.getAttribute('viewBox').split(' ')
        width, height = viewbox[2:]

        # Handle overrides in case they were not encoded.
        settings = self.plot_settings
        if settings['width'] != -1:
            if settings['height'] == -1:
                height = height * settings['width'] / width
            width = settings['width']
        if settings['height'] != -1:
            if settings['width'] == -1:
                width = width * settings['height'] / height
            height = settings['height']

        svg.setAttribute('width', '%dpx' % int(width))
        svg.setAttribute('height', '%dpx' % int(height))
        return svg.toxml()

    def _create_repl(self):
        cmd = self.executable
        if 'octave-cli' not in cmd:
            version_cmd = [self.executable, '--version']
            version = subprocess.check_output(version_cmd).decode('utf-8')
            if 'version 4' in version:
                cmd += ' --no-gui'
        # Interactive mode prevents crashing on Windows on syntax errors.
        # Delay sourcing the "~/.octaverc" file in case it displays a pager.
        cmd += ' --interactive --quiet --no-init-file'
        orig_prompt = u('octave.*>')
        change_prompt = u("PS1('{0}'); PS2('{1}')")

        repl = REPLWrapper(cmd, orig_prompt, change_prompt,
                           stdin_prompt_regex=re.compile(r'\A[\w]+>>? '))
        repl.linesep = '\n'
        return repl

    def _get_executable(self):
        """Find the best octave executable.
        """
        executable = os.environ.get('OCTAVE_EXECUTABLE', None)
        if not executable or not which(executable):
            if which('octave-cli'):
                executable = 'octave-cli'
            elif which('octave'):
                executable = 'octave'
            else:
                msg = ('Octave Executable not found, please add to path or set'
                       '"OCTAVE_EXECUTABLE" environment variable')
                raise OSError(msg)
        return executable
