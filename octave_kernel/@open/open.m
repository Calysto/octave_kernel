## -*- texinfo -*-
## @deftypefn {Function File} open (@var{fname})
## Display the path to @var{fname} instead of opening it in an editor.
##
## This override replaces the default editor-launch behavior with inline
## path output, preventing the kernel from hanging in a headless
## environment (e.g., Jupyter).
## @seealso{which, type}
## @end deftypefn

function open (fname)
  if (nargin == 0)
    error ("open: wrong number of arguments");
  end
  p = which (fname);
  if (! isempty (p))
    disp (p)
  elseif (exist (fname, "file"))
    disp (fname)
  else
    warning ("open: '%s' not found", fname);
  end
endfunction
