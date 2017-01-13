## -*- texinfo -*-
## @deftypefn  {Function File} kbhit ()
## @deftypefnx {Function File} kbhit (1)
## Read a single keystroke from the keyboard.
##
## If called with an argument, don't wait for a keypress.
##
## For example,
##
##      x = kbhit ();
##
## will set X to the next character typed at the keyboard as soon as
## it is typed.
##
##      x = kbhit (1);
##
## is identical to the above example, but doesn't wait for a keypress,
## returning the empty string if no key is available.
##
##seealso{input, pause}
## @end deftypefn

function kbhit(n)
    disp('**WARNING Kernel ignoring unsupported function `kbhit`');
endfunction;
