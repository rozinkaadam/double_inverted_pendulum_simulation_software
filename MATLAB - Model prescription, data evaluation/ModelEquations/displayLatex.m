function displayLatex(varargin)
    % displayLatex: Displays LaTeX expressions in a MATLAB Live Script text block
    %
    % Syntax:
    %   displayLatex(expr1, expr2, ..., exprN)
    %
    % Example:
    %   displayLatex('\frac{d}{dt}\left(\frac{\partial L}{\partial \dot{\theta}}\right)', '- \frac{\partial L}{\partial \theta} = q');
    
    % Check if there is any input
    if nargin < 1
        error('At least one LaTeX expression must be provided!');
    end
    
    % Start building the LaTeX expression
    latexString = '\['; % Begin mathematical environment
    
    % Concatenate the input expressions
    for i = 1:nargin
        if i > 1
            latexString = strcat(latexString, '\quad'); % Add spacing between expressions
        end
        latexString = strcat(latexString, varargin{i});
    end
    
    % Close the mathematical environment
    latexString = strcat(latexString, '\]');
    
    % Print to the text block
    fprintf('%s\n', latexString); % Copy the output to the text block
end
