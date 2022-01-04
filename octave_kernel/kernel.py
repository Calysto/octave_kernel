from __future__ import print_function

import atexit
import codecs
import glob
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from xml.dom import minidom

from traitlets import Dict, Unicode
from metakernel import MetaKernel, ProcessMetaKernel, REPLWrapper, u, MetaKernelApp
from metakernel.pexpect import which
from IPython.display import Image, SVG

from ._version import __version__


STDIN_PROMPT = '__stdin_prompt>'
STDIN_PROMPT_REGEX = re.compile(r'\A.+?%s|debug> ' % STDIN_PROMPT)
HELP_LINKS = [
    {
        'text': "GNU Octave",
        'url': "https://www.gnu.org/software/octave/support.html",
    },
    {
        'text': "Octave Kernel",
        'url': "https://github.com/Calysto/octave_kernel",
    },

] + MetaKernel.help_links


def get_kernel_json():
    """Get the kernel json for the kernel.
    """
    here = os.path.dirname(__file__)
    default_json_file = os.path.join(here, 'kernel.json')
    json_file = os.environ.get('OCTAVE_KERNEL_JSON', default_json_file)
    with open(json_file) as fid:
        data = json.load(fid)
    data['argv'][0] = sys.executable
    return data


class OctaveKernel(ProcessMetaKernel):
    app_name = 'octave_kernel'
    implementation = 'Octave Kernel'
    implementation_version = __version__
    language = 'octave'
    help_links = HELP_LINKS
    kernel_json = Dict(get_kernel_json()).tag(config=True)
    cli_options = Unicode('').tag(config=True)
    inline_toolkit = Unicode('qt').tag(config=True)

    _octave_engine = None
    _language_version = None

    @property
    def language_version(self):
        if self._language_version:
            return self._language_version
        ver = self.octave_engine.eval('version', silent=True)
        ver = self._language_version = ver.split()[-1]
        return ver

    @property
    def language_info(self):
        return {'mimetype': 'text/x-octave',
                'name': 'octave',
                'file_extension': '.m',
                'version': self.language_version,
                'help_links': HELP_LINKS}

    @property
    def banner(self):
        msg = 'Octave Kernel v%s running GNU Octave v%s'
        return msg % (__version__, self.language_version)

    @property
    def octave_engine(self):
        if self._octave_engine:
            return self._octave_engine
        self._octave_engine = OctaveEngine(plot_settings=self.plot_settings,
                                           defer_startup=True,
                                           error_handler=self.Error,
                                           stdin_handler=self.raw_input,
                                           stream_handler=self.Print,
                                           cli_options=self.cli_options,
                                           inline_toolkit=self.inline_toolkit,
                                           logger=self.log)
        return self._octave_engine

    def makeWrapper(self):
        """Start an Octave process and return a :class:`REPLWrapper` object.
        """
        return self.octave_engine.repl

    def do_execute_direct(self, code, silent=False):
        if code.strip() in ['quit', 'quit()', 'exit', 'exit()']:
            self._octave_engine = None
            self.do_shutdown(True)
            return
        if not self.octave_engine._has_startup:
            self.octave_engine._startup()
        val = ProcessMetaKernel.do_execute_direct(self, code, silent=silent)
        if not silent:
            try:
                plot_dir = self.octave_engine.make_figures()
            except Exception as e:
                self.Error(e)
                return val
            if plot_dir:
                for image in self.octave_engine.extract_figures(plot_dir, True):
                    self.Display(image)
        return val

    def get_kernel_help_on(self, info, level=0, none_on_fail=False):
        obj = info.get('help_obj', '')
        if not obj or len(obj.split()) > 1:
            if none_on_fail:
                return None
            else:
                return ""
        return self.octave_engine.eval('help %s' % obj, silent=True)

    def Print(self, *args, **kwargs):
        # Ignore standalone input hook displays.
        out = []
        for arg in args:
            if arg.strip() == STDIN_PROMPT:
                return
            if arg.strip().startswith(STDIN_PROMPT):
                arg = arg.replace(STDIN_PROMPT, '')
            out.append(arg)
        super(OctaveKernel, self).Print(*out, **kwargs)

    def raw_input(self, text):
        # Remove the stdin prompt to restore the original prompt.
        text = text.replace(STDIN_PROMPT, '')
        return super(OctaveKernel, self).raw_input(text)

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
                 line_handler=None,
                 stdin_handler=None, plot_settings=None,
                 inline_toolkit='qt', defer_startup = False,
                 cli_options='', logger=None):
        if not logger:
            logger = logging.getLogger(__name__)
            logging.basicConfig()
        self.logger = logger
        self.executable = self._get_executable()
        self.cli_options = cli_options
        self.inline_toolkit = inline_toolkit
        self.repl = self._create_repl()
        self.error_handler = error_handler
        self.stream_handler = stream_handler
        self.stdin_handler = stdin_handler or sys.stdin
        self.line_handler = line_handler
        self._has_startup = False
        self._plot_settings = plot_settings
        if not defer_startup:
            self._startup()
        atexit.register(self._cleanup)

    @property
    def plot_settings(self):
        return self._plot_settings

    @plot_settings.setter
    def plot_settings(self, settings):
        settings = settings or dict(backend='inline')
        self._plot_settings = settings

        # Remove "None" keys so we can use setdefault below.
        keys = ['format', 'backend', 'width', 'height', 'resolution',
                'backend', 'name', 'plot_dir']
        for key in keys:
            if key in settings and settings.get(key, None) is None:
                del settings[key]

        settings.setdefault('format', 'png')
        settings.setdefault('backend', 'inline')
        settings.setdefault('width', -1)
        settings.setdefault('height', -1)
        settings.setdefault('resolution', 0)
        settings.setdefault('name', 'Figure')
        settings.setdefault('plot_dir', None)

        cmds = []
        if settings['backend'] == 'inline':
            cmds.append("graphics_toolkit('%s')" % self.inline_toolkit)
            cmds.append("set(0, 'defaultfigurevisible', 'off');")
        elif settings['backend'].startswith('inline:'):
            backend = settings['backend'].replace('inline:', '')
            cmds.append("graphics_toolkit('%s')" % backend)
            cmds.append("set(0, 'defaultfigurevisible', 'off');")
        else:
            cmds.append("set(0, 'defaultfigurevisible', 'on');")
            if settings['backend'] != 'default':
                cmds.append("graphics_toolkit('%s');" % settings['backend'])
            else:
                cmds.append("graphics_toolkit('%s');" % self._default_toolkit)

        self.eval('\n'.join(cmds))

    def eval(self, code, timeout=None, silent=False):
        """Evaluate code using the engine.
        """
        stream_handler = None if silent else self.stream_handler
        line_handler = None if silent else self.line_handler

        if self.logger:
            self.logger.debug('Octave eval:')
            self.logger.debug(code)
        try:
            resp = self.repl.run_command(code.rstrip(),
                                         timeout=timeout,
                                         stream_handler=stream_handler,
                                         line_handler=line_handler,
                                         stdin_handler=self.stdin_handler)
            resp = resp.replace(STDIN_PROMPT, '')
            if self.logger and resp:
                self.logger.debug(resp)
            return resp
        except KeyboardInterrupt:
            return self._interrupt(silent=True)
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
        if not settings['backend'].startswith('inline'):
            self.eval('drawnow("expose");')
            if not plot_dir:
                return
        fmt = settings['format']
        res = settings['resolution']
        wid = settings['width']
        hgt = settings['height']
        name = settings['name']
        plot_dir = plot_dir or tempfile.mkdtemp(dir=settings['plot_dir'])
        plot_dir = plot_dir.replace(os.path.sep, '/')

        # Do not overwrite any existing plot files.
        spec = os.path.join(plot_dir, '%s*' % name)
        start = len(glob.glob(spec))

        make_figs = '_make_figures("%s", "%s", "%s", %d, %d, %d, %d)'
        make_figs = make_figs % (plot_dir, fmt, name, wid, hgt, res, start)
        resp = self.eval(make_figs, silent=True)
        msg = 'Inline plot failed, consider trying another graphics toolkit\n'
        if resp and 'error:' in resp:
            resp = msg + resp
            if self.error_handler:
                self.error_handler(resp)
            else:
                raise Exception(resp)
        return plot_dir

    def extract_figures(self, plot_dir, remove=False):
        """Get a list of IPython Image objects for the created figures.

        Parameters
        ----------
        plot_dir: str
            The directory in which to create the plots.
        remove: bool, optional.
            Whether to remove the plot directory after saving.
        """
        images = []
        spec = os.path.join(plot_dir, '%s*' % self.plot_settings['name'])
        for fname in reversed(glob.glob(spec)):
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
        if remove:
            shutil.rmtree(plot_dir, True)
        return images

    def _startup(self):
        self._has_startup = True
        cwd = os.getcwd().replace(os.path.sep, '/')
        self._default_toolkit = self.eval('graphics_toolkit', silent=True).split()[-1]
        cmd = 'more off; source ~/.octaverc; cd("%s");%s'
        self.eval(cmd % (cwd, self.repl.prompt_change_cmd), silent=True)
        here = os.path.realpath(os.path.dirname(__file__))
        self.eval('addpath("%s")' % here.replace(os.path.sep, '/'))
        self.plot_settings = self._plot_settings

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
        width, height = int(width), int(height)

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

        svg.setAttribute('width', '%dpx' % width)
        svg.setAttribute('height', '%dpx' % height)
        return svg.toxml()

    def _create_repl(self):
        cmd = self.executable
        if 'octave' not in cmd:
            version_cmd = [self.executable, '--version']
            version = subprocess.check_output(version_cmd).decode('utf-8')
            if 'version 4' in version:
                cmd += ' --no-gui'
        # Interactive mode prevents crashing on Windows on syntax errors.
        # Delay sourcing the "~/.octaverc" file in case it displays a pager.
        cmd += ' --interactive --quiet --no-init-file '

        # Add cli options provided by the user.
        cmd += os.environ.get('OCTAVE_CLI_OPTIONS', self.cli_options)

        orig_prompt = u('octave.*>')
        change_prompt = u("PS1('{0}'); PS2('{1}')")

        repl = REPLWrapper(cmd, orig_prompt, change_prompt,
                           stdin_prompt_regex=STDIN_PROMPT_REGEX,
                           force_prompt_on_continuation=True)
        if os.name == 'nt':
            repl.child.crlf = '\n'
        repl.interrupt = self._interrupt
        # Remove the default 50ms delay before sending lines.
        repl.child.delaybeforesend = None
        return repl

    def _interrupt(self, continuation=False, silent=False):
        if os.name == 'nt':
            msg = '** Warning: Cannot interrupt Octave on Windows'
            if self.stream_handler:
                self.stream_handler(msg)
            elif self.logger:
                self.logger.warn(msg)
            return self._interrupt_expect(silent)

        return REPLWrapper.interrupt(self.repl, continuation=continuation)

    def _interrupt_expect(self, silent):
        repl = self.repl
        child = repl.child
        expects = [repl.prompt_regex, child.linesep]
        expected = uuid.uuid4().hex
        repl.sendline('disp("%s");' % expected)
        if repl.prompt_emit_cmd:
            repl.sendline(repl.prompt_emit_cmd)
        lines = []
        while True:
            # Prevent a keyboard interrupt from breaking this up.
            while True:
                try:
                    pos = child.expect(expects)
                    break
                except KeyboardInterrupt:
                    pass
            if pos == 1:  # End of line received
                line = child.before
                if silent:
                    lines.append(line)
                else:
                    self.stream_handler(line)
            else:
                line = child.before
                if line.strip() == expected:
                    break
                if len(line) != 0:
                    # prompt received, but partial line precedes it
                    if silent:
                        lines.append(line)
                    else:
                        self.stream_handler(line)
        return '\n'.join(lines)

    def _get_executable(self):
        """Find the best octave executable.
        """
        # Attempt to get the octave executable
        executable = os.environ.get('OCTAVE_EXECUTABLE', None)
        if executable:
            fullpath = which(executable)
            if 'snap' not in fullpath:
                executable = fullpath
                if 'octave' not in executable:
                    raise OSError('OCTAVE_EXECUTABLE does not point to an octave file, please see README')
        else:
            executable = which('octave')
            if not executable:
                raise OSError('octave not found, please see README')
        return executable.replace(os.path.sep, '/')

    def _cleanup(self):
        """Clean up resources used by the session.
        """
        try:
            self.repl.terminate()
        except Exception as e:
            self.logger.debug(str(e))
        workspace = os.path.join(os.getcwd(), 'octave-workspace')
        if os.path.exists(workspace):
            os.remove(workspace)
