function _input_hook()
    %% Meant to be used as `add_input_event_hook(@_input_hook)`
    %% to notify a remote caller of a stdin request.
    disp('__stdin_prompt>');
endfunction
