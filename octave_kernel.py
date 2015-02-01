from __future__ import print_function

from metakernel import MetaKernel, ProcessMetaKernel, REPLWrapper, u
from IPython.display import Image
from subprocess import check_output
import os
import tempfile
from shutil import rmtree


PLOT_DIR = tempfile.mkdtemp()

__version__ = '0.1'


# make plotting inline only - using png


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
    set(0, 'defaultfigurevisible', 'off');
    graphics_toolkit('gnuplot');

    function make_figs(figdir)
        figHandles = get(0, 'children');
        for fig=1:length(figHandles)
            h = figHandles(fig);
            filename = fullfile(figdir, ['OctaveFig', sprintf('%%03d', fig)]);
            saveas(h, [filename, '.png']);
            disp(filename);
            close(fig);
        end;
    endfunction;
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
            orig_prompt = 'octave.*>'
            prompt_cmd = None
            change_prompt = "PS1('{0}'); PS2('{1}')"

        self._first = True
        return REPLWrapper('octave', orig_prompt, change_prompt,
                           prompt_emit_cmd=prompt_cmd)

    def do_execute_direct(self, code):
        if self._first:
            super(OctaveKernel, self).do_execute_direct(self._setup)
            self._first = False

        resp = super(OctaveKernel, self).do_execute_direct(code)

        plot_dir = tempfile.mkdtemp()
        make_figs = 'make_figs("%s")' % plot_dir
        super(OctaveKernel, self).do_execute_direct(make_figs)
        for fname in os.listdir(plot_dir):
            im = Image(filename=os.path.join(plot_dir, fname))
            self.Display(im)

        return resp

    def get_kernel_help_on(self, info, level=0, none_on_fail=False):
        obj = info.get('help_obj', '')
        if not obj or len(obj.split()) > 1:
            if none_on_fail:
                return None
            else:
                return ""
        resp = self.wrapper.run_command('more off; help %s' % obj)
        return resp

    def get_completions(self, info):
        """
        Get completions from kernel based on info dict.
        """
        cmd = 'completion_matches("%s")' % info['obj']
        resp = self.wrapper.run_command(cmd)
        return resp.splitlines()


if __name__ == '__main__':
    from IPython.kernel.zmq.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=OctaveKernel)
