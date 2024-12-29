function s_plot(dataset_to_plot, max_timestamp, display_names, plot_title, horizontal_axis_title, vertical_axis_title, varargin)
%S_PLOT Plot multiple datasets with optional y-axis limits
%   This function plots the provided datasets up to the specified maximum
%   timestamp, with optional y-axis limits.
%   
%   Parameters:
%   dataset_to_plot - Cell array containing datasets ({value, timestamp})
%   max_timestamp - Maximum timestamp for data filtering
%   display_names - Cell array of names for the legend
%   plot_title - Title of the plot
%   horizontal_axis_title - Label for the x-axis
%   vertical_axis_title - Label for the y-axis
%   varargin - Optional parameter specifying y-axis limits as [y_min, y_max]

% Check the size of the cell array
num_datasets = size(dataset_to_plot, 1);

% Check if display names match the number of datasets
if length(display_names) ~= num_datasets
    error('The length of display_names does not match the number of rows in dataset_to_plot.');
end

% Parse optional y-axis limits
if ~isempty(varargin)
    y_limits = varargin{1};
    if length(y_limits) ~= 2 || ~isnumeric(y_limits)
        error('y-axis limits must be a numeric array with two elements [y_min, y_max].');
    end
else
    y_limits = [];
end

% Initialize the plot
figure;
hold on;
for i = 1:num_datasets
    % Extract the current dataset
    current_data = dataset_to_plot{i, 1}; % 1x2 cell: {value, timestamp}

    % Extract values and timestamps
    values = current_data{1};      % Value list
    timestamps = current_data{2}; % Timestamp list

    % Filter data by maximum timestamp
    valid_indices = timestamps <= max_timestamp; % Logical indices
    filtered_values = values(valid_indices);      % Filtered values
    filtered_timestamps = timestamps(valid_indices); % Filtered timestamps

    % Plot the data with the corresponding display name
    plot(filtered_timestamps, filtered_values, '-', 'DisplayName', display_names{i});
end

% Format the plot
xlabel(horizontal_axis_title);
ylabel(vertical_axis_title);
title(plot_title);
legend('show');
grid on;

% Apply y-axis limits if specified
if ~isempty(y_limits)
    ylim(y_limits);
end

hold off;
end
