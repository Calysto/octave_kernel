## -*- texinfo -*-
## @deftypefn  {Function File} pause ()
## @deftypefnx {Function File} pause (@var{n})
## Suspend the execution of the program for N seconds.
##
## N is a positive real value and may be a fraction of a second.
##
## If invoked without an input arguments then the program is suspended
## until a character is typed.
##
## The following example prints a message and then waits 5 seconds
## before clearing the screen.
##
##      fprintf (stderr, "wait please...\n");
##      pause (5);
##      clc;
##
##seealso{kbhit, sleep}
## @end deftypefn

function pause(n)
    if (nargin == 0)
        input('Paused, enter any value to continue');
    elseif (n > 5)
        msg = '** Pausing execution for %0.1f seconds.';
        if (!ispc())
            msg = strcat(msg, '  Interrupt the kernel to abort pause.');
        end
        disp(sprintf(msg, n));
        builtin('pause', n);
    else
        builtin('pause', n)
    end
    
endfunction
