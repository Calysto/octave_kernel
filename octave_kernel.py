from __future__ import print_function

from metakernel import MetaKernel, ProcessMetaKernel, REPLWrapper, u
from IPython.display import Image, SVG
from subprocess import check_output
import os
import tempfile
from shutil import rmtree


__version__ = '0.10.0'


class OctaveKernel(ProcessMetaKernel):
    implementation = 'Octave Kernel'
    implementation_version = __version__,
    language = 'octave'
    language_version = '0.1',
    banner = "Matlab Kernel"
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
            banner = check_output(['octave', '--version'])
            self._banner = banner.decode('utf-8')
        return self._banner

    def makeWrapper(self):
        """Start a bash shell and return a :class:`REPLWrapper` object.
        Note that this is equivalent :function:`metakernel.pyexpect.bash`,
        but is used here as an example of how to be cross-platform.
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

        return REPLWrapper('octave', orig_prompt, change_prompt,
                           prompt_emit_cmd=prompt_cmd)

    def do_execute_direct(self, code):
        if self._first:
            self._first = False
            self.handle_plot_settings()
            super(OctaveKernel, self).do_execute_direct(self._setup)

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
            rmtree(plot_dir)

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
        settings.setdefault('format', 'png')
        settings.setdefault('size', '560,420')

        cmds = []

        if settings['backend'] == 'inline':
            cmds.append("set(0, 'defaultfigurevisible', 'off');")
            cmds.append("graphics_toolkit('gnuplot');")
        else:
            cmds.append("set(0, 'defaultfigurevisible', 'on');")
            cmds.append("graphics_toolkit('%s');" % settings['backend'])

        if isinstance(settings['size'], tuple):
            width, height = settings['size']
        else:
            try:
                width, height = settings['size'].split(',')
                width, height = int(width), int(height)
            except Exception as e:
                self.Error(e)
                width, height = 560, 420

        size = "set(0, 'defaultfigurepaperposition', [0 0 %s %s]);"
        cmds.append(size % (width / 150., height / 150.))

        self.do_execute_direct('\n'.join(cmds))

    def _make_figs(self, plot_dir):
            cmd = """
            figHandles = get(0, 'children');
            for fig=1:length(figHandles);
                h = figHandles(fig);
                filename = fullfile('%s', ['OctaveFig', sprintf('%%03d', fig)]);
                saveas(h, [filename, '.png']);
                close(h);
            end;
            """ % plot_dir
            super(OctaveKernel, self).do_execute_direct(cmd.replace('\n', ''))

if __name__ == '__main__':
    from IPython.kernel.zmq.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=OctaveKernel)
