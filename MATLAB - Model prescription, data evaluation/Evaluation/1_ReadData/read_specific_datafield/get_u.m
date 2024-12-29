function [result_list] = get_u(data_matrix, index_list)
% extract_data_elements - Returns the elements of data_matrix based on index_list.
%
% Inputs:
%   - data_matrix: A cell array containing data similar to phi_matrix.
%   - index_list: A cell array or char array containing the indices,
%     for example, "M1_a.1.2", "M4_d.4.1".
%
% Outputs:
%   - result_list: A cell array containing the data extracted based on the indices.

    % Initialize the result container
    result_list = cell(length(index_list), 1);

    % Iterate through the elements of index_list
    for i = 1:length(index_list)
        % Parse the current index
        index_str = index_list{i};
        
        % For example: "M1_a.1.2" -> [row_index, column_index]
        tokens = regexp(index_str, 'M(\d+)_(\w)', 'tokens');
        
        if isempty(tokens)
            error('Invalid index format: %s', index_str);
        end
        
        % Extract row and column indices
        measurement = str2double(tokens{1}{1}); % Measurement number (e.g., 1)
        variant = double(tokens{1}{2}) - double('a') + 1; % Variant 
        
        % Check index boundaries
        if measurement > size(data_matrix, 1) || variant > size(data_matrix, 2)
            error('Index out of bounds: %s', index_str);
        end
        
        % Access the inner element of the data_matrix at the specified index
        inner_data = data_matrix{measurement, variant};
        if isempty(inner_data)
            error('Empty data at the specified index: %s', index_str);
        end
        
        inner_dat = inner_data{1, 2};
        [filtered_values, adjusted_timestamps] = normalize_and_filter_data({inner_dat.stateVars.phi_np_array_list.timestamp(1), inner_dat.mouse_input.q_array_list.x_m, inner_dat.mouse_input.q_array_list.timestamp});
    
        result_list{i} = {filtered_values / 0.00572917, adjusted_timestamps};
    end
end
