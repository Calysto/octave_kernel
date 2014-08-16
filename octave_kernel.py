from IPython.kernel.zmq.kernelbase import Kernel
from IPython.utils.path import locate_profile
from IPython.core.oinspect import Inspector, cast_unicode
from oct2py import Oct2PyError, octave

import os
import signal
from subprocess import check_output
import re
import logging
import tempfile
import base64
from glob import glob
from shutil import rmtree
from xml.dom import minidom

__version__ = '0.4'

version_pat = re.compile(r'version (\d+(\.\d+)+)')


class OctaveKernel(Kernel):
    implementation = 'octave_kernel'
    implementation_version = __version__
    language = 'octave'

    @property
    def language_version(self):
        m = version_pat.search(self.banner)
        return m.group(1)

    _banner = None

    @property
    def banner(self):
        if self._banner is None:
            self._banner = check_output(['octave',
                                         '--version']).decode('utf-8')
        return self._banner

    def __init__(self, **kwargs):
        Kernel.__init__(self, **kwargs)
        # Signal handlers are inherited by forked processes,
        # and we can't easily reset it from the subprocess.
        # Since kernelapp ignores SIGINT except in message handlers,
        # we need to temporarily reset the SIGINT handler here
        # so that octave and its children are interruptible.
        sig = signal.signal(signal.SIGINT, signal.SIG_DFL)
        try:
            self.octavewrapper = octave
            octave.restart()
            # make sure the kernel is ready at startup
            octave.eval('1')
        finally:
            signal.signal(signal.SIGINT, sig)

        self.inspector = Inspector()
        self.inspector.set_active_scheme("Linux")

        self.log.setLevel(logging.INFO)

        try:
            self.hist_file = os.path.join(locate_profile(),
                                          'octave_kernel.hist')
        except IOError:
            self.hist_file = None
            self.log.warn('No default profile found, history unavailable')

        self.max_hist_cache = 1000
        self.hist_cache = []
        self.docstring_cache = {}
        self.help_cache = {}
        self.inline = False

    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=False):
        """Execute a line of code in Octave."""
        code = code.strip()
        abort_msg = {'status': 'abort',
                     'execution_count': self.execution_count}

        if code and store_history:
            self.hist_cache.append(code)

        if not code or code == 'keyboard' or code.startswith('keyboard('):
            return {'status': 'ok', 'execution_count': self.execution_count,
                    'payload': [], 'user_expressions': {}}

        elif (code == 'exit' or code.startswith('exit(')
                or code == 'quit' or code.startswith('quit(')):
            # TODO: exit gracefully here
            self.do_shutdown(False)
            return abort_msg

        elif code == 'restart' or code.startswith('restart('):
            self.octavewrapper.restart()
            return abort_msg

        elif code == '%inline':
            self.inline = not self.inline
            output = "Inline is set to %s" % self.inline
            stream_content = {'name': 'stdout', 'data': output}
            self.send_response(self.iopub_socket, 'stream', stream_content)
            return abort_msg

        elif code.endswith('?') or code.startswith('?'):
            self._get_help(code)
            return abort_msg

        try:
            if self.inline:
                code = '__inline=1;close all;' + code
            output = self.eval(code)
            if self.inline:
                plot_dir, plot_format = self._post_call()

        except Oct2PyError as e:
            return self._handle_error(str(e))

        if not silent:
            stream_content = {'name': 'stdout', 'data': output}
            self.send_response(self.iopub_socket, 'stream', stream_content)
            if self.inline:
                self._handle_figures(plot_dir, plot_format)

        if output == 'Octave Session Interrupted':
            return abort_msg

        return {'status': 'ok', 'execution_count': self.execution_count,
                'payload': [], 'user_expressions': {}}

    def do_complete(self, code, cursor_pos):
        """Get code completions using Octave's 'completion_matches'"""

        code = code[:cursor_pos]
        default = {'matches': [], 'cursor_start': 0,
                   'cursor_end': cursor_pos, 'metadata': dict(),
                   'status': 'ok'}

        if code[-1] == ' ':
            return default

        tokens = code.replace(';', ' ').split()
        if not tokens:
            return default
        token = tokens[-1]

        start = cursor_pos - len(token)
        cmd = 'completion_matches("%s")' % token
        try:
            output = self.octavewrapper.eval(str(cmd), timeout=5)
        except Oct2PyError as e:
            self.log.error(e)
            return default

        matches = []

        if output:
            matches = output.split()
            for item in dir(self.octavewrapper):
                if item.startswith(token) and not item in matches:
                    matches.append(item)

        matches.extend(_complete_path(token))

        return {'matches': matches, 'cursor_start': start,
                'cursor_end': cursor_pos, 'metadata': dict(),
                'status': 'ok'}

    def do_inspect(self, code, cursor_pos, detail_level=0):
        """If the code ends with a (, try to return a calltip docstring"""
        default = {'status': 'aborted', 'data': dict(), 'metadata': dict()}
        if (not code or not len(code) >= cursor_pos or
                not code[cursor_pos - 1] == '('):
            return default

        else:
            token = code[:cursor_pos - 1].replace(';', '').split()[-1]
            if token in self.docstring_cache:
                docstring = self.docstring_cache[token]

            elif token in self.help_cache:
                docstring = self.help_cache[token]['docstring']

            else:
                try:
                    info = self. _get_octave_info(token, detail_level)
                except Exception as e:
                    self.log.error(e)
                    return default

                docstring = info['docstring']
                self.docstring_cache[token] = docstring

            if docstring:
                data = {'text/plain': docstring}
                return {'status': 'ok', 'data': data, 'metadata': dict()}

        return default

    def do_history(self, hist_access_type, output, raw, session=None,
                   start=None, stop=None, n=None, pattern=None, unique=False):
        """Access history at startup.
        """
        if not self.hist_file:
            return {'history': []}

        if not os.path.exists(self.hist_file):
            with open(self.hist_file, 'wb') as fid:
                fid.write('')

        with open(self.hist_file, 'rb') as fid:
            history = fid.readlines()

        history = history[:self.max_hist_cache]
        self.hist_cache = history
        self.log.debug('**HISTORY:')
        self.log.debug(history)
        history = [(None, None, h) for h in history]

        return {'history': history}

    def do_shutdown(self, restart):
        """Shut down the app gracefully, saving history.
        """
        self.log.debug("**Shutting down")

        if restart:
            self.octavewrapper.restart()

        else:
            self.octavewrapper.exit()

        if self.hist_file:
            with open(self.hist_file, 'wb') as fid:
                data = '\n'.join(self.hist_cache[-self.max_hist_cache:])
                fid.write(data.encode('utf-8'))

        return {'status': 'ok', 'restart': restart}

    def eval(self, code):
        output = ''

        try:
            output = self.octavewrapper.eval(str(code))

        except KeyboardInterrupt:
            self.octavewrapper._session.proc.send_signal(signal.SIGINT)
            output = 'Octave Session Interrupted'

        except Oct2PyError as e:
            raise Oct2PyError(str(e))

        except Exception as e:
            self.log.error(e)
            self.octavewrapper.restart()
            output = 'Uncaught Exception, Restarting Octave'

        if output is None:
            output = ''
        output = str(output)

        return output

    def _post_call(self):
        '''Generate plots in a temporary directory.'''
        plot_dir = tempfile.mkdtemp().replace('\\', '/')

        if os.name == 'nt':
            plot_format = 'svg'
        else:
            plot_format = 'png'

        post_call = """
        for f = __oct2py_figures
          outfile = sprintf('%s/__ipy_oct_fig_%%03d.png', f);
              try
                print(f, outfile, '-d%s', '-tight');
                close(f);
              end
        end
        """ % (plot_dir, plot_format)

        self.eval(post_call)
        return plot_dir, plot_format

    def _get_help(self, code):
        if code.startswith('??') or code.endswith('??'):
            detail_level = 1
        else:
            detail_level = 0

        code = code.replace('?', '')
        tokens = code.replace(';', ' ').split()
        if not tokens:
            return
        token = tokens[-1]

        if token in self.help_cache:
            info = self.help_cache[token]

        else:
            try:
                info = self. _get_octave_info(token, detail_level)
            except Exception as e:
                self.log.error(e)
                return
            if info['type_name'] == 'built-in function':
                self.help_cache[token] = info
                if token in self.docstring_cache:
                    del self.docstring_cache[token]

        output = _get_printable_info(self.inspector, info, detail_level)
        stream_content = {'name': 'stdout', 'data': output}
        self.send_response(self.iopub_socket, 'stream', stream_content)

    def _handle_error(self, err):
        if 'parse error:' in err:
            err = 'Parse Error'

        elif 'Octave returned:' in err:
            err = err[err.index('Octave returned:'):]
            err = err[len('Octave returned:'):].lstrip()

        elif 'Syntax Error' in err:
            err = 'Syntax Error'

        stream_content = {'name': 'stdout', 'data': err.strip()}
        self.send_response(self.iopub_socket, 'stream', stream_content)

        return {'status': 'error', 'execution_count': self.execution_count,
                'ename': '', 'evalue': err, 'traceback': []}

    def _handle_figures(self, plot_dir, plot_format):

        width, height = 640, 480

        _mimetypes = {'png': 'image/png',
                      'svg': 'image/svg+xml',
                      'jpg': 'image/jpeg',
                      'jpeg': 'image/jpeg'}

        images = []
        for imgfile in glob("%s/*" % plot_dir):
            with open(imgfile, 'rb') as fid:
                images.append(fid.read())
        rmtree(plot_dir)

        plot_mime_type = _mimetypes.get(plot_format, 'image/png')

        for image in images:
            if plot_format == 'svg':
                image = _fix_gnuplot_svg_size(image, size=(width, height))
            else:
                image = base64.b64encode(image).decode('ascii')
            data = {plot_mime_type: image}
            metadata = {plot_mime_type: {'width': width, 'height': height}}

            self.log.info('Sending a plot')
            stream_content = {'source': 'octave_kernel', 'data': data,
                              'metadata': metadata}
            self.send_response(self.iopub_socket, 'display_data',
                               stream_content)

    def _get_octave_info(self, obj, detail_level):
        info = dict(argspec=None, base_class=None, call_def=None,
                    call_docstring=None, class_docstring=None,
                    definition=None, docstring='', file=None,
                    found=False, init_definition=None,
                    init_docstring=None, isalias=0, isclass=None,
                    ismagic=0, length=None, name='', namespace=None,
                    source=None, string_form=None, type_name='')

        oc = self.octavewrapper

        if obj in dir(oc):
            obj = getattr(oc, obj)
            return self.inspector.info(obj, detail_level=detail_level)

        try:
            exist = oc.eval('exist "%s"' % obj, timeout=1)
        except Oct2PyError:
            return info

        if exist == 0:
            return info

        try:
            help_str = oc.eval('help %s' % obj, timeout=1)
        except Oct2PyError:
            help_str = None

        try:
            type_str = oc.type(obj, timeout=0.5)[0].strip()
        except Oct2PyError:
            type_str = ''

        try:
            cls_str = oc.eval("class(%s)" % obj, timeout=0.5)
        except Oct2PyError:
            cls_str = ''

        if type_str:
            type_first_line = type_str.splitlines()[0]
            type_str = '\n'.join(type_str.splitlines()[1:])
        else:
            type_first_line = ''

        try:
            var = oc.pull(obj, timeout=1)
        except Oct2PyError:
            var = None

        string_form = obj

        if not var is None:
            help_str = '%s is a variable of type %s.' % (obj, cls_str)
            type_str = cls_str
            string_form = str(var)

        info['found'] = True
        info['docstring'] = help_str or type_first_line
        info['type_name'] = type_str
        info['source'] = help_str
        info['string_form'] = string_form

        if type_first_line.rstrip().endswith('.m'):
            info['file'] = type_first_line.split()[-1]
            info['type_name'] = 'function'
            info['source'] = type_str

            if not help_str:
                info['docstring'] = None

        return info


def _get_printable_info(inspector, info, detail_level=0):
    displayfields = []

    def add_fields(fields):
        for title, key in fields:
            field = info[key]
            if field is not None:
                displayfields.append((title, field.rstrip()))

    add_fields(inspector.pinfo_fields1)
    add_fields(inspector.pinfo_fields2)
    add_fields(inspector.pinfo_fields3)

    # Source or docstring, depending on detail level and whether
    # source found.
    if detail_level > 0 and info['source'] is not None:
        source = cast_unicode(info['source'])
        displayfields.append(("Source",  source))

    elif info['docstring'] is not None:
        displayfields.append(("Docstring", info["docstring"]))

    # Info for objects:
    else:
        add_fields(inspector.pinfo_fields_obj)

    # Finally send to printer/pager:
    if displayfields:
        return inspector._format_fields(displayfields)


def _listdir(root):
    "List directory 'root' appending the path separator to subdirs."
    res = []
    for name in os.listdir(root):
        path = os.path.join(root, name)
        if os.path.isdir(path):
            name += os.sep
        res.append(name)
    return res


def _complete_path(path=None):
    """Perform completion of filesystem path.

    http://stackoverflow.com/questions/5637124/tab-completion-in-pythons-raw-input
    """
    if not path:
        return _listdir('.')
    dirname, rest = os.path.split(path)
    tmp = dirname if dirname else '.'
    res = [os.path.join(dirname, p)
           for p in _listdir(tmp) if p.startswith(rest)]
    # more than one match, or single match which does not exist (typo)
    if len(res) > 1 or not os.path.exists(path):
        return res
    # resolved to a single directory, so return list of files below it
    if os.path.isdir(path):
        return [os.path.join(path, p) for p in _listdir(path)]
    # exact file match terminates this completion
    return [path + ' ']


def _fix_gnuplot_svg_size(image, size=None):
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
        (svg,) = minidom.parseString(image).getElementsByTagName('svg')
        viewbox = svg.getAttribute('viewBox').split(' ')

        if size is not None:
            width, height = size
        else:
            width, height = viewbox[2:]

        svg.setAttribute('width', '%dpx' % width)
        svg.setAttribute('height', '%dpx' % height)
        return svg.toxml()

if __name__ == '__main__':
    from IPython.kernel.zmq.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=OctaveKernel)
