function [filtered_values, adjusted_timestamps] = filter_and_adjust_timestamps(data)
    % Input:
    % data - 1x3 cell array
    %   data{1} - minimum timestamp (double scalar)
    %   data{2} - list of values (1xN double array)
    %   data{3} - list of timestamps (1xN double array)
    %
    % Output:
    % filtered_values - Values that meet the minimum timestamp condition
    % adjusted_timestamps - Corresponding timestamps with the smallest timestamp set to zero

    % Validate the input
    if length(data) ~= 3
        error('The input must be a 1x3 cell array.');
    end
    
    % Extract the data
    min_timestamp = data{1};
    values = data{2};
    timestamps = data{3};
    
    % Validate the types and sizes of the data
    if ~isscalar(min_timestamp) || ~isnumeric(min_timestamp)
        error('The minimum timestamp must be a double scalar.');
    end
    if ~isvector(values) || ~isnumeric(values)
        error('The list of values must be a numeric vector.');
    end
    if ~isvector(timestamps) || ~isnumeric(timestamps)
        error('The list of timestamps must be a numeric vector.');
    end

    % Handle differing lengths
    len_values = length(values);
    len_timestamps = length(timestamps);

    if len_values < len_timestamps
        % If values is shorter, pad it with the last value
        values = [values, repmat(values(end), 1, len_timestamps - len_values)];
    elseif len_values > len_timestamps
        % If values is longer, truncate excess elements
        values = values(1:len_timestamps);
    end
    
    % Filter based on the minimum timestamp
    valid_indices = timestamps >= min_timestamp; % Logical indexing
    
    % Filtered data
    filtered_values = values(valid_indices);
    filtered_timestamps = timestamps(valid_indices);
    
    % Adjust timestamps: subtract the smallest timestamp
    if ~isempty(filtered_timestamps)
        adjusted_timestamps = filtered_timestamps - filtered_timestamps(1);
    else
        adjusted_timestamps = []; % If no valid timestamps
    end
end
