function resultsTable = calculateStatisticsTableAngle(dataCell1, dataCell2, runNames)
    % Validations
    if ~iscell(dataCell1) || isempty(dataCell1) || ~iscell(dataCell2) || isempty(dataCell2)
        error('Both dataCell1 and dataCell2 must be non-empty cell arrays');
    end
    if ~iscell(runNames) || length(runNames) ~= length(dataCell1) || length(runNames) ~= length(dataCell2)
        error('Input runNames must be a cell array with the same length as dataCell1 and dataCell2');
    end

    % Initialize statistical metrics with units
    statNames = {'Standard Deviation (rad)', 'RMS (rad)', 'Trapz Integral (rad*s)'};
    numStats = length(statNames);
    numRuns = length(dataCell1);

    % Initialize the results table
    results = cell(numRuns, numStats * 2); % Double columns for the two dataCells

    % Iterate through the runs
    for i = 1:numRuns
        % First dataCell
        pair1 = dataCell1{i};
        if length(pair1) ~= 2
            error('Each cell in dataCell1 must contain a (data, timestamp) pair.');
        end
        data1 = pair1{1};
        timestamp1 = pair1{2};
        if length(data1) ~= length(timestamp1)
            error('Data and timestamp vectors in dataCell1 must have the same length.');
        end
        results{i, 1} = std(data1);                 % Standard deviation
        results{i, 3} = rms(data1);                 % RMS
        results{i, 5} = trapz(timestamp1, abs(data1)); % Trapezoidal integral

        % Second dataCell
        pair2 = dataCell2{i};
        if length(pair2) ~= 2
            error('Each cell in dataCell2 must contain a (data, timestamp) pair.');
        end
        data2 = pair2{1};
        timestamp2 = pair2{2};
        if length(data2) ~= length(timestamp2)
            error('Data and timestamp vectors in dataCell2 must have the same length.');
        end
        results{i, 2} = std(data2);                 % Standard deviation
        results{i, 4} = rms(data2);                 % RMS
        results{i, 6} = trapz(timestamp2, abs(data2)); % Trapezoidal integral
    end

    % Create new column names
    newStatNames = cell(1, numStats * 2);
    for j = 1:numStats
        newStatNames{j * 2 - 1} = [statNames{j} ' - DataCell1'];
        newStatNames{j * 2} = [statNames{j} ' - DataCell2'];
    end

    % Create the results table
    resultsTable = cell2table(results, 'RowNames', cellstr(runNames), 'VariableNames', newStatNames);
end
