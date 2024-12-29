function [filename_matrix] = get_filepaths(parent_dir)
% Reads the files in the current directory
files = dir(fullfile(parent_dir, '*.csv')); % Search only for .csv files in this directory

% Organize file names
file_names = {files.name}; % All file names in a cell array
max_measurement = 0;
max_variant = 0;

% Analyze files starting with the letter 'M'
for i = 1:length(file_names)
    % Split file name: M{number}_{variant}.csv
    name_parts = regexp(file_names{i}, 'M(\d+)_(\w)\.csv', 'tokens');
    if ~isempty(name_parts)
        measurement = str2double(name_parts{1}{1});
        variant = double(name_parts{1}{2}) - double('a') + 1; % 'a' = 1, 'b' = 2, etc.
        max_measurement = max(max_measurement, measurement);
        max_variant = max(max_variant, variant);
    end
end

% Initialize the result matrix
filename_matrix = cell(max_measurement, max_variant);

% Fill the matrix with the appropriate file paths
for i = 1:length(file_names)
    name_parts = regexp(file_names{i}, 'M(\d+)_(\w)\.csv', 'tokens');
    if ~isempty(name_parts)
        measurement = str2double(name_parts{1}{1});
        variant = double(name_parts{1}{2}) - double('a') + 1;
        filename_matrix{measurement, variant} = fullfile(parent_dir, file_names{i});
    end
end

% Verify: display the contents of filename_matrix
disp(filename_matrix);
end
