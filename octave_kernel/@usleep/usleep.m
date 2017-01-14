## -*- texinfo -*-
## @deftypefn {Function File} usleep (@var{microseconds})
## Suspend the execution of the program for the given number of
## microseconds.
##
## On systems where it is not possible to sleep for periods of time
## less than one second, 'usleep' will pause the execution for 'round
## (MICROSECONDS / 1e6)' seconds.
##
##seealso{sleep, pause}
## @end deftypefn

function usleep(varargin)
    usec = varargin{1};
    if (usec > 5e6)
        msg = '** Sleeping for %0.1f seconds.';
        if (!ispc())
            msg = strcat(msg, '  Interrupt the kernel to abort sleep.');
        end
        disp(sprintf(msg, usec / 1e6));
    end
    builtin('usleep', usec);
endfunction
