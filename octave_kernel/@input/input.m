## -*- texinfo -*-
## @deftypefn  {Built-in Function} {@var{ans} =} input (@var{prompt})
## @deftypefnx {Built-in Function} {@var{ans} =} input (@var{prompt}, "s")
## Print @var{prompt} and wait for user input.
## 
## For example,
## 
## @example
## input ("Pick a number, any number! ")
## @end example
## 
## @noindent
## prints the prompt
## 
## @example
## Pick a number, any number!
## @end example
## 
## @noindent
## and waits for the user to enter a value.  The string entered by the user
## is evaluated as an expression, so it may be a literal constant, a variable
## name, or any other valid Octave code.
## 
## The number of return arguments, their size, and their class depend on the
## expression entered.
## 
## If you are only interested in getting a literal string value, you can call
## @code{input} with the character string @qcode{"s"} as the second argument.
## This tells Octave to return the string entered by the user directly, without
## evaluating it first.
## 
## Because there may be output waiting to be displayed by the pager, it is a
## good idea to always call @code{fflush (stdout)} before calling @code{input}.
##  This will ensure that all pending output is written to the screen before
## your prompt.
## @seealso{yes_or_no, kbhit, pause, menu, listdlg}
## @end deftypefn

function ans = input(varargin)
    if (nargin > 0)
        varargin{1} = strcat(varargin{1}, '__stdin_prompt>');
    end
    ans = builtin('input', varargin{:});
endfunction;
