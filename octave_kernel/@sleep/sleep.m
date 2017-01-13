## -*- texinfo -*-
## @deftypefn {Function File} sleep (@var{seconds})
## Suspend the execution of the program for the given number of
##   seconds.
##
##seealso{usleep, pause}
## @end deftypefn

function sleep(varargin)
    seconds = varargin{1};
    if (seconds > 5)
        msg = sprintf('** Sleeping for %0.1f seconds.  Interrupt the kernel to abort sleep.', seconds);
            disp(msg);
    end
    builtin('sleep', seconds);
endfunction
