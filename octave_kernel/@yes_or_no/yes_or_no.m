## -*- texinfo -*-
## @deftypefn {Built-in Function} {@var{ans} =} yes_or_no ("@var{prompt}")
## Ask the user a yes-or-no question. 
##
## Return logical true if the answer is yes or false if the answer is no.
## 
## Takes one argument, @var{prompt}, which is the string to display when asking
## the question.  @var{prompt} should end in a space; @code{yes-or-no} adds the
## string @samp{(yes or no) } to it.  The user must confirm the answer with
## @key{RET} and can edit it until it has been confirmed.
## @seealso{input}
## @end deftypefn

function ans = yes_or_no(varargin)
  if (nargin == 0)
    varargin = {''};
  end
  if (nargin > 1)
    builtin('yes_or_no', varargin{:});

  else
    prompt = strcat(varargin{1}, ' (yes_or_no) __stdin_prompt>');
    while (1)
      resp = input(prompt, 's');
      if (strcmp(resp, 'yes') == 1)
        ans = true;
        break;

      elseif (strcmp(resp, 'no') == 1)
        ans = false;
        break;

      end;
      prompt = 'Please answer yes or no.';
    end;
  end;

end;
