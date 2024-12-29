function lin_matrix = linearizeMatrix(matrixFunc, vars, expansionPoint, taylorOrder)
    % LINEARIZEMATRIX Linearizes a matrix function around a given point with Taylor expansion
    % 
    % Inputs:
    % - matrixFunc: A symbolic matrix (e.g., sym matrix function)
    % - vars: Variables in the function (as a symbolic vector, e.g., [x, y])
    % - expansionPoint: Point of expansion (e.g., [x0, y0])
    % - taylorOrder: Order of the Taylor expansion (e.g., 1 for linearization)
    %
    % Outputs:
    % - lin_matrix: Linearized matrix as a symbolic matrix

    % Validate inputs
    if nargin < 4
        error('All inputs (matrixFunc, vars, expansionPoint, taylorOrder) are required.');
    end
    
    if length(vars) ~= length(expansionPoint)
        error('The number of variables must match the number of expansion points.');
    end
    
    % Convert matrixFunc to symbolic if not already
    if ~isa(matrixFunc, 'sym')
        error('matrixFunc must be a symbolic matrix.');
    end

    % Perform Taylor expansion for each element in the matrix
    [rows, cols] = size(matrixFunc);
    lin_matrix = sym(zeros(rows, cols)); % Initialize linearized matrix
    
    for i = 1:rows
        for j = 1:cols
            element = matrixFunc(i, j); % Current matrix element
            lin_matrix(i, j) = taylor(element, vars, ...
                                       'ExpansionPoint', expansionPoint, ...
                                       'Order', taylorOrder + 1); % Taylor expansion
        end
    end

    % Simplify the result for clarity
    lin_matrix = simplify(lin_matrix);
end
