function freq95Values = plotFrequencySpectrum(dataCell, runNames, varargin)
% PLOTFREQUENCYSPECTRUM Plots frequency spectrum for multiple runs with optional y-axis limits
%   This function computes and plots the frequency spectrum for multiple
%   datasets provided in a cell array, with an option to set y-axis limits.
%   It also returns a vector of freq95 values, representing the frequency
%   where 95% of the energy is contained for each run.
%   
%   Parameters:
%   dataCell - Cell array containing (data, timestamp) pairs for each run
%   runNames - Cell array of run names for labeling the subplots
%   varargin - Optional parameter specifying y-axis limits as [y_min, y_max]
%   
%   Returns:
%   freq95Values - Array of freq95 values for each run

    % Input validation
    if ~iscell(dataCell) || isempty(dataCell)
        error('Input dataCell must be a non-empty cell array');
    end
    if ~iscell(runNames) || length(runNames) ~= length(dataCell)
        error('Input runNames must be a cell array with the same length as dataCell');
    end

    numRuns = length(dataCell);
    freq95Values = zeros(1, numRuns); % Initialize freq95 array

    % Parse optional y-axis limits
    if ~isempty(varargin)
        y_limits = varargin{1};
        if length(y_limits) ~= 2 || ~isnumeric(y_limits)
            error('y-axis limits must be a numeric array with two elements [y_min, y_max].');
        end
    else
        y_limits = [];
    end

    % Initialize figure
    figure;
    for i = 1:numRuns
        pair = dataCell{i};
        if length(pair) ~= 2
            error('Each cell in dataCell must contain a (data, timestamp) pair.');
        end

        % Extract data and timestamps
        data = pair{1};
        timestamp = pair{2};

        % Ensure data and timestamps have the same length
        if length(data) ~= length(timestamp)
            error('Data and timestamp vectors must have the same length.');
        end

        % Determine sampling frequency
        dt = mean(diff(timestamp));
        fs = 1 / dt; % Sampling frequency

        % Perform Fourier transform
        N = length(data);
        fftResult = fft(data);
        f = fs * (0:(N/2)) / N; % Frequency axis
        P = abs(fftResult / N);
        P = P(1:N/2+1);
        P(2:end-1) = 2 * P(2:end-1); % Normalize

        % Plot spectrum
        subplot(numRuns, 1, i);
        plot(f, P, 'b'); % Spectrum plot
        grid on;
        ylabel(runNames{i});
        xlim([0 3.5]); % Limit to 0-5 Hz

        % Highlight significant frequency band (95% energy)
        cumulativeEnergy = cumsum(P.^2);
        totalEnergy = cumulativeEnergy(end);
        freq95 = f(find(cumulativeEnergy >= 0.95 * totalEnergy, 1));
        freq95Values(i) = freq95; % Store freq95 value
        xline(freq95, 'k--', 'LineWidth', 1.5, 'DisplayName', '95% Energy');

        % Apply y-axis limits if specified
        if ~isempty(y_limits)
            ylim(y_limits);
        end

        if i == numRuns
            xlabel('Frequency (Hz)');
        end
    end
end
