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
        disp('** Pausing execution indefinitely.  Interrupt the kernel to continue'
            );
        builtin('pause');
    elseif (n > 5)
        msg = sprintf('** Pausing execution for %0.1f seconds.  Interrupt the kernel to abort pause.', n);
        disp(msg);
        builtin('pause', n);
    else
        builtin('pause', n)
    end
    
endfunction
