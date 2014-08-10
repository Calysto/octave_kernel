from IPython.kernel.zmq.kernelbase import Kernel
from IPython.utils.path import locate_profile
from IPython.core.oinspect import Inspector, cast_unicode
from oct2py import Oct2PyError, octave

import os
import signal
from subprocess import check_output
import re
import logging

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

        elif code == 'restart':
            self.octavewrapper.restart()
            return abort_msg

        elif code.endswith('?') or code.startswith('?'):
            self._get_help(code)
            return abort_msg

        interrupted = False
        try:
            output = self.octavewrapper._eval(str(code))

        except KeyboardInterrupt:
            self.octavewrapper._session.proc.send_signal(signal.SIGINT)
            interrupted = True
            output = 'Octave Session Interrupted'

        except Oct2PyError as e:
            return self._handle_error(str(e))

        except Exception:
            self.octavewrapper.restart()
            output = 'Uncaught Exception, Restarting Octave'

        else:
            if output is None:
                output = ''
            output = str(output)
            if output == 'Octave Session Interrupted':
                interrupted = True

        if not silent:
            stream_content = {'name': 'stdout', 'data': output}
            self.send_response(self.iopub_socket, 'stream', stream_content)

        if interrupted:
            return abort_msg

        return {'status': 'ok', 'execution_count': self.execution_count,
                'payload': [], 'user_expressions': {}}

    def do_complete(self, code, cursor_pos):
        """Get code completions using Octave's 'completion_matches'"""
        self.log.info(code)
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
        output = self.octavewrapper._eval(str(cmd))
        matches = []

        if output:
            matches = output.split()
            for item in dir(self.octavewrapper):
                if item.startswith(token) and not item in matches:
                    matches.append(item)

        self.log.info(token)
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
                self.log.info(token)
                info = _get_octave_info(self.octavewrapper,
                                        self.inspector,
                                        token, detail_level)
                self.log.info(info)
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
            self.octavewrapper.close()

        if self.hist_file:
            with open(self.hist_file, 'wb') as fid:
                fid.write('\n'.join(self.hist_cache[-self.max_hist_cache:]))

        return {'status': 'ok', 'restart': restart}

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
            info = _get_octave_info(self.octavewrapper, self.inspector,
                                    token, detail_level)
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


def _get_octave_info(octave, inspector, obj, detail_level):
    info = dict(argspec=None, base_class=None, call_def=None,
                call_docstring=None, class_docstring=None,
                definition=None, docstring=None, file=None,
                found=False, init_definition=None,
                init_docstring=None, isalias=0, isclass=None,
                ismagic=0, length=None, name='', namespace=None,
                source=None, string_form=None, type_name='')

    oc = octave

    if obj in dir(oc):
        obj = getattr(oc, obj)
        return inspector.info(obj, detail_level=detail_level)

    exist = oc.run('exist "%s"' % obj)
    if exist == 0:
        return info

    try:
        help_str = oc.run('help %s' % obj)
    except Oct2PyError:
        help_str = None

    type_str = oc.type(obj)[0].strip()

    try:
        cls_str = oc.run("class(%s)" % obj)
    except Oct2PyError:
        cls_str = ''

    type_first_line = type_str.splitlines()[0]
    type_str = '\n'.join(type_str.splitlines()[1:])

    is_var = 'is a variable' in type_first_line
    if is_var:
        var = oc.get(obj)

    info['found'] = True
    info['docstring'] = help_str or type_first_line
    info['type_name'] = cls_str if is_var else 'built-in function'
    info['source'] = help_str
    info['string_form'] = obj if not is_var else str(var)

    if type_first_line.rstrip().endswith('.m'):
        info['file'] = type_first_line.split()[-1]
        info['type_name'] = 'function'
        info['source'] = type_str

        if not help_str:
            info['docstring'] = None

    return info


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


if __name__ == '__main__':
    from IPython.kernel.zmq.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=OctaveKernel)
