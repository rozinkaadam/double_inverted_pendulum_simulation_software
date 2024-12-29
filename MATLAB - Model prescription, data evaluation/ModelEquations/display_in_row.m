function latex_string = display_in_row(vars)
    % The function's input is a cell array containing the values of variables
    % Example call: display_in_row({rA, rS1, rB});

    % Check if the input is a cell array
    if ~iscell(vars)
        error('The input must be a cell array.');
    end

    % Initialize the LaTeX row string
    latex_string = '';

    % Iterate through the values of the variables
    for i = 1:length(vars)
        val = vars{i};

        % Handle symbolic expressions or numbers
        if isa(val, 'sym')
            val_str = latex(val); % Convert symbolic variable to LaTeX code
        else
            val_str = num2str(val); % Convert number to a string
        end

        % Append to the LaTeX string
        latex_string = strcat(latex_string, sprintf('$%s$ & ', val_str));
    end

    % Remove the last '&' character
    latex_string = latex_string(1:end-2);
end
