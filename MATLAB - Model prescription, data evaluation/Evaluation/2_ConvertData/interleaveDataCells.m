function combinedDataCell = interleaveDataCells(dataCell1, dataCell2)
    % Check: same length
    if length(dataCell1) ~= length(dataCell2)
        error('The two dataCells must have the same number of elements.');
    end

    % Initialization
    numPairs = length(dataCell1);
    combinedDataCell = cell(2 * numPairs, 1);

    % Interleaving: alternating order
    for i = 1:numPairs
        combinedDataCell{2 * i - 1} = dataCell1{i};
        combinedDataCell{2 * i} = dataCell2{i};
    end
end
