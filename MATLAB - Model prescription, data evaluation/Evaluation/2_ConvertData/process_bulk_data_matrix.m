function data_matrix = process_bulk_data_matrix(filepaths)
    % Determine the dimensions of the matrix
    [num_measurements, num_variants] = size(filepaths);
    % Initialize the result matrix (cell array, as it will hold mixed data types)
    data_matrix = cell(num_measurements, num_variants);
    % Iterate through the filepaths matrix
    for i = 1:num_measurements
        for j = 1:num_variants
            filepath = filepaths{i, j}; % Content of the current cell
            disp(filepath)
            % Check if the cell is not empty
            if ~isempty(filepath)
                % Process the file
                try
                    [firstPhiValues, data] = shrink_phi_array(parseCSV(filepath));
                    % Store the results in the data_matrix
                    data_matrix{i, j} = {firstPhiValues, data};
                catch ME
                    % On error, display the message and continue
                    fprintf('An error occurred while processing the file: %s\n', filepath);
                    fprintf('Error message: %s\n', ME.message);
                    data_matrix{i, j} = []; % Store an empty cell in case of error
                end
            else
                % If the cell is empty, store an empty element
                data_matrix{i, j} = [];
            end
        end
    end
end
