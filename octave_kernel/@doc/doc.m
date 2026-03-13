## -*- texinfo -*-
## @deftypefn  {Function File} doc ()
## @deftypefnx {Function File} doc (@var{topic})
## Display documentation for @var{topic} inline.
##
## This override replaces the default GUI documentation browser with
## inline text output, preventing the kernel from hanging in a headless
## environment (e.g., Jupyter).
## @seealso{help}
## @end deftypefn

function doc (varargin)
  if (nargin == 0)
    help
  else
    help (varargin{1})
  end
endfunction
