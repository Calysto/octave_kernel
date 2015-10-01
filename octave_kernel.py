from __future__ import print_function

from metakernel import MetaKernel, ProcessMetaKernel, REPLWrapper, u
from IPython.display import Image, SVG
import subprocess
import os
import sys
import tempfile


__version__ = '0.12.10'


class OctaveKernel(ProcessMetaKernel):
    implementation = 'Octave Kernel'
    implementation_version = __version__,
    language = 'octave'
    language_version = '0.1',
    banner = "Octave Kernel"
    language_info = {
        'mimetype': 'text/x-octave',
        'name': 'octave_kernel',
        'file_extension': '.m',
        'help_links': MetaKernel.help_links,
    }

    _setup = """
    more off;
    set(0, 'defaultfigurepaperunits', 'inches');
    set(0, 'defaultfigureunits', 'inches');
    """

    _first = True

    _banner = None

    @property
    def banner(self):
        if self._banner is None:
            banner = subprocess.check_output(['octave', '--version'])
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

        executable = os.environ.get('OCTAVE_EXECUTABLE', 'octave')
        try:
            info = subprocess.check_output([executable, '--version'])
            if 'version 4' in info.decode('utf-8').lower():
                executable += ' --no-gui'
        except OSError:  # pragma: no cover
            pass

        return REPLWrapper(executable, orig_prompt, change_prompt,
                           prompt_emit_cmd=prompt_cmd)

    def do_execute_direct(self, code):
        if self._first:
            self._first = False
            if sys.platform == 'darwin':
                self.plot_settings['format'] = 'svg'
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

        resp = super(OctaveKernel, self).do_execute_direct(code)

        if self.plot_settings.get('backend', None) == 'inline':
            plot_dir = tempfile.mkdtemp()
            self._make_figs(plot_dir)
            for fname in os.listdir(plot_dir):
                filename = os.path.join(plot_dir, fname)
                try:
                    if fname.lower().endswith('.svg'):
                        im = SVG(filename)
                    else:
                        im = Image(filename)
                    self.Display(im)
                except Exception as e:
                    self.Error(e)

        return resp

    def get_kernel_help_on(self, info, level=0, none_on_fail=False):
        obj = info.get('help_obj', '')
        if not obj or len(obj.split()) > 1:
            if none_on_fail:
                return None
            else:
                return ""
        resp = self.do_execute_direct('help %s' % obj)
        return resp

    def get_completions(self, info):
        """
        Get completions from kernel based on info dict.
        """
        cmd = 'completion_matches("%s")' % info['obj']
        resp = self.do_execute_direct(cmd)
        return resp.splitlines()

    def handle_plot_settings(self):
        """Handle the current plot settings"""
        settings = self.plot_settings
        if settings.get('format', None) is None:
            settings.clear()
        settings.setdefault('backend', 'inline')
        settings.setdefault('format', 'svg')
        settings.setdefault('size', '560,420')

        cmds = []

        self._plot_fmt = settings['format']

        if settings['backend'] == 'inline':
            cmds.append("set(0, 'defaultfigurevisible', 'off');")
            cmds.append("graphics_toolkit('gnuplot');")
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
            except Exception as e:
                self.Error('Error setting plot settings: %s' % e)

        size = "set(0, 'defaultfigurepaperposition', [0 0 %s %s]);"
        cmds.append(size % (width / 150., height / 150.))

        self.do_execute_direct('\n'.join(cmds))

    def _make_figs(self, plot_dir):
            cmd = """
            figHandles = get(0, 'children');
            for fig=1:length(figHandles);
                h = figHandles(fig);
                filename = fullfile('%s', ['OctaveFig', sprintf('%%03d', fig)]);
                saveas(h, [filename, '.%s']);
                close(h);
            end;
            """ % (plot_dir, self._plot_fmt)
            super(OctaveKernel, self).do_execute_direct(cmd.replace('\n', ''))

if __name__ == '__main__':
    try:
        from ipykernel.kernelapp import IPKernelApp
    except ImportError:
        from IPython.kernel.zmq.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=OctaveKernel)
