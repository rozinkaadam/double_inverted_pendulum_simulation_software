function [normalized_values, normalized_timestamps] = normalize_and_filter_data(data)
    % Input:
    % data - 1x3 cell array
    %   data{1} - minimum timestamp (double scalar)
    %   data{2} - list of values (1xN double array)
    %   data{3} - list of timestamps (1xN double array)
    %
    % Output:
    % normalized_values - Normalized values that meet the minimum timestamp condition
    % normalized_timestamps - Normalized timestamps (first timestamp subtracted)

    % Validate the input
    if length(data) ~= 3
        error('The input must be a 1x3 cell array.');
    end
    
    % Extract the data
    min_timestamp = data{1};
    values = data{2};
    timestamps = data{3};
    
    % Validate the data types
    if ~isscalar(min_timestamp) || ~isnumeric(min_timestamp)
        error('The minimum timestamp must be a double scalar.');
    end
    if ~isvector(values) || ~isnumeric(values)
        error('The list of values must be a numeric vector.');
    end
    if ~isvector(timestamps) || ~isnumeric(timestamps)
        error('The list of timestamps must be a numeric vector.');
    end
    
    % Check if lengths match
    len_values = length(values);
    len_timestamps = length(timestamps);
    if len_values ~= len_timestamps
        % Length of the longer list
        max_length = max(len_values, len_timestamps);
        
        % Pad the shorter list
        if len_values < max_length
            values = [values, repmat(values(end), 1, max_length - len_values)];
        elseif len_timestamps < max_length
            timestamps = [timestamps, repmat(timestamps(end), 1, max_length - len_timestamps)];
        end
    end
    
    % Filter based on the minimum timestamp
    valid_indices = timestamps >= min_timestamp; % Logical indexing
    
    % Filtered data
    filtered_values = values(valid_indices);
    filtered_timestamps = timestamps(valid_indices);
    
    % Normalization (subtract the first value and timestamp)
    if ~isempty(filtered_timestamps)
        first_timestamp = filtered_timestamps(1);
        first_value = filtered_values(1);
        
        normalized_timestamps = filtered_timestamps - first_timestamp;
        normalized_values = filtered_values - first_value;
    else
        % If no valid data, return empty outputs
        normalized_timestamps = [];
        normalized_values = [];
    end
end
