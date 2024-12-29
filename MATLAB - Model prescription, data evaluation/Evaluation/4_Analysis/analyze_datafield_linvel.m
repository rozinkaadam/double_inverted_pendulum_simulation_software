function resultsTable = analyze_datafield_linvel(dataCell, runNames)
    % Validations
    if ~iscell(dataCell) || isempty(dataCell)
        error('Input dataCell must be a non-empty cell array');
    end
    if ~iscell(runNames) || length(runNames) ~= length(dataCell)
        error('Input runNames must be a cell array with the same length as dataCell');
    end

    % Statistical metrics initialization with units
    statNames = {'Standard Deviation of Speed (m/s)', 'RMS Speed (m/s)', 'Speed Energy (m)'};
    numStats = length(statNames);
    numRuns = length(dataCell);

    % Initialize the table matrix
    statsMatrix = zeros(numRuns, numStats);

    % Iterate through the runs
    for i = 1:numRuns
        pair = dataCell{i};
        if length(pair) ~= 2
            error('Each cell in dataCell must contain a (data, timestamp) pair.');
        end

        % Extract the data and timestamps
        data = pair{1};
        timestamp = pair{2};

        % Validation: data and timestamps must have the same length
        if length(data) ~= length(timestamp)
            error('Data and timestamp vectors must have the same length.');
        end

        % Calculate speed
        dt = mean(diff(timestamp));
        speed = diff(data) / dt;

        % Calculations
        statsMatrix(i, 1) = std(speed);                     % Standard deviation of speed
        statsMatrix(i, 2) = rms(speed);                     % RMS speed
        statsMatrix(i, 3) = trapz(timestamp(1:end-1), abs(speed)); % Speed energy usage
    end

    % Create the results table with units and no numbering
    resultsTable = array2table(statsMatrix, 'RowNames', cellstr(runNames), 'VariableNames', statNames);
end
