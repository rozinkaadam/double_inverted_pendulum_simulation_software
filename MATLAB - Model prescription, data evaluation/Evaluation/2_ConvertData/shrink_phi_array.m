function [firstValues, updatedStruct] = shrink_phi_array(dataStruct)
    % Check if stateVars.phi_np_array_list exists
    if ~isfield(dataStruct, 'stateVars') || ...
       ~isfield(dataStruct.stateVars, 'phi_np_array_list')
        error('The stateVars.phi_np_array_list is not found in the structure.');
    end

    % Fields to process
    fieldsToExtract = {
        'x.phi_1', 'x.phi_2', 'x.dphi_1', 'x.dphi_2', ...
        'dx.dphi_1', 'dx.dphi_2', 'dx.ddphi_1', 'dx.ddphi_2', ...
        'F1', 'ddq'
    };

    % Initialize structures for return values
    firstValues = struct();
    updatedStruct = dataStruct; % Copy of the original structure

    % Iterate through the specified fields
    for i = 1:length(fieldsToExtract)
        fieldPath = strsplit(fieldsToExtract{i}, '.'); % Split by dots
        [firstValue, updatedStruct.stateVars.phi_np_array_list] = ...
            extractAndRemove(updatedStruct.stateVars.phi_np_array_list, fieldPath);
        firstValues.(strjoin(fieldPath, '_')) = firstValue;
    end
end

function [firstValue, updatedStruct] = extractAndRemove(nestedStruct, fieldPath)
    % Recursively extracts and removes the first value of the specified field
    currentField = fieldPath{1};

    if length(fieldPath) == 1
        % If we reach the target field
        if isfield(nestedStruct, currentField) && ~isempty(nestedStruct.(currentField))
            % Save the first value
            firstValue = nestedStruct.(currentField)(1);
            % Remove the first value
            nestedStruct.(currentField) = nestedStruct.(currentField)(2:end);
        else
            % If the field does not exist or is empty
            firstValue = NaN;
        end
    else
        % If there are further sub-sections
        if isfield(nestedStruct, currentField)
            [firstValue, nestedStruct.(currentField)] = ...
                extractAndRemove(nestedStruct.(currentField), fieldPath(2:end));
        else
            % If the sub-section does not exist
            firstValue = NaN;
        end
    end

    % Return the updated structure
    updatedStruct = nestedStruct;
end
