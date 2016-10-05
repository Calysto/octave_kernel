from __future__ import print_function

from metakernel import MetaKernel, ProcessMetaKernel, REPLWrapper, u
from metakernel.pexpect import which
from IPython.display import Image, SVG
import subprocess
from xml.dom import minidom
import os
import shutil
import sys
import tempfile


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

    _setup = """
    more off;
    """

    _first = True

    _banner = None

    _executable = None

    @property
    def executable(self):
        if self._executable:
            return self._executable
        executable = os.environ.get('OCTAVE_EXECUTABLE', None)
        if not executable or not which(executable):
            if which('octave-cli'):
                self._executable = 'octave-cli'
                return self._executable
            elif which('octave'):
                self._executable = 'octave'
                return self._executable
            else:
                msg = ('Octave Executable not found, please add to path or set'
                       '"OCTAVE_EXECUTABLE" environment variable')
                raise OSError(msg)
        else:
            self._executable = executable
            return executable

    @property
    def banner(self):
        if self._banner is None:
            banner = subprocess.check_output([self.executable, '--version'])
            self._banner = banner.decode('utf-8')
        return self._banner

    def makeWrapper(self):
        """Start an Octave process and return a :class:`REPLWrapper` object.
        """
        if os.name == 'nt':
            orig_prompt = u(chr(3))
            prompt_cmd = u('disp(char(3))')
            change_prompt = None
        else:
            orig_prompt = u('octave.*>')
            prompt_cmd = None
            change_prompt = u("PS1('{0}'); PS2('{1}')")

        self._first = True

        executable = self.executable
        if 'version 4' in self.banner:
            executable += ' --no-gui'

        wrapper = REPLWrapper(executable, orig_prompt, change_prompt,
                prompt_emit_cmd=prompt_cmd)
        wrapper.child.linesep = '\n'
        return wrapper

    def do_execute_direct(self, code):
        if self._first:
            self._first = False
            self.handle_plot_settings()
            super(OctaveKernel, self).do_execute_direct(self._setup)
            if os.name != 'nt':
                msg = ('may not be able to display plots properly '
                       'without gnuplot, please install it '
                       '(gnuplot-x11 on Linux)')
                try:
                    subprocess.check_call(['gnuplot', '--version'])
                except subprocess.CalledProcessError:
                    self.Error(msg)

        super(OctaveKernel, self).do_execute_direct(code, self.Print)
        if self.plot_settings.get('backend', None) == 'inline':
            plot_dir = tempfile.mkdtemp()
            self._make_figs(plot_dir)
            width, height = 0, 0
            for fname in os.listdir(plot_dir):
                filename = os.path.join(plot_dir, fname)
                try:
                    if fname.lower().endswith('.svg'):
                        im = SVG(filename)
                        size = self.plot_settings['size']
                        if not (isinstance(size, tuple)):
                            size = 560, 420
                        width, height = size
                        width, height = int(width), int(height)
                        im.data = self._fix_gnuplot_svg_size(im.data,
                            size=(width, height))
                    else:
                        im = Image(filename)
                    self.Display(im)
                except Exception as e:
                    import traceback
                    traceback.print_exc(file=sys.__stderr__)
                    self.Error(e)
            shutil.rmtree(plot_dir, True)

    def get_kernel_help_on(self, info, level=0, none_on_fail=False):
        obj = info.get('help_obj', '')
        if not obj or len(obj.split()) > 1:
            if none_on_fail:
                return None
            else:
                return ""
        resp = super(OctaveKernel, self).do_execute_direct('help %s' % obj)
        return str(resp)

    def get_completions(self, info):
        """
        Get completions from kernel based on info dict.
        """
        cmd = 'completion_matches("%s")' % info['obj']
        resp = super(OctaveKernel, self).do_execute_direct(cmd)
        return str(resp).splitlines()

    def handle_plot_settings(self):
        """Handle the current plot settings"""
        settings = self.plot_settings
        if settings.get('format', None) is None:
            settings.clear()
        settings.setdefault('backend', 'inline')
        if sys.platform == 'darwin':
            settings.setdefault('format', 'svg')
        else:
            settings.setdefault('format', 'png')
        settings.setdefault('format', 'png')
        settings.setdefault('size', '560,420')
        settings.setdefault('resolution', 150.)

        cmds = []

        self._plot_fmt = settings['format']

        if settings['backend'] == 'inline':
            cmds.append("set(0, 'defaultfigurevisible', 'off');")
            cmds.append("graphics_toolkit('gnuplot');")
            if sys.platform == 'darwin':
                cmds.append('setenv("GNUTERM","X11");')
        else:
            cmds.append("set(0, 'defaultfigurevisible', 'on');")
            cmds.append("graphics_toolkit('%s');" % settings['backend'])

        width, height = 560, 420
        if isinstance(settings['size'], tuple):
            width, height = settings['size']
        elif settings['size']:
            try:
                width, height = settings['size'].split(',')
                width, height = int(width), int(height)
                settings['size'] = width, height
            except Exception as e:
                self.Error('Error setting plot settings: %s' % e)

        size = "set(0, 'defaultfigureposition', [0 0 %s %s]);"
        cmds.append(size % (width, height))

        self.do_execute_direct('\n'.join(cmds))

    def _make_figs(self, plot_dir):
        fmt = self.plot_settings['format']
        res = self.plot_settings['resolution']
        cmd = """
        _figHandles = get(0, 'children');
        for _fig=1:length(_figHandles),
            _handle = _figHandles(_fig);
            _filename = fullfile('%(plot_dir)s', ['OctaveFig', sprintf('%%03d.%(fmt)s', _fig)]);
            try,
               _image = double(get(get(get(_handle,'children'),'children'),'cdata'));
               _clim = get(get(_handle,'children'),'clim');
               _image = _image - _clim(1);
               _image = _image ./ (_clim(2) - _clim(1));
               imwrite(uint8(_image*255), _filename);
            catch,
               print(_handle, _filename, '-r%(res)s');
            end,
            close(_handle);
        end;
        """ % locals()
        super(OctaveKernel, self).do_execute_direct(cmd.replace('\n', ''))

    def _fix_gnuplot_svg_size(self, image, size=None):
        """
        GnuPlot SVGs do not have height/width attributes.  Set
        these to be the same as the viewBox, so that the browser
        scales the image correctly.

        Parameters
        ----------
        image : str
            SVG data.
        size : tuple of int
            Image width, height.

        """
        # Minidom does not support parseUnicode, so it must be decoded
        # to accept unicode characters
        parsed = minidom.parseString(image.encode('utf-8'))
        (svg,) = parsed.getElementsByTagName('svg')
        viewbox = svg.getAttribute('viewBox').split(' ')

        if size is not None and size[0] is not None:
            width, height = size
        else:
            width, height = viewbox[2:]

        svg.setAttribute('width', '%dpx' % int(width))
        svg.setAttribute('height', '%dpx' % int(height))
        return svg.toxml()
