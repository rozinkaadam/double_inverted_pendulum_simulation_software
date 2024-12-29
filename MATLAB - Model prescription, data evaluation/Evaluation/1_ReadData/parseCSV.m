function [dataStruct] = parseCSV(filename)
    % Open the file
    fileID = fopen(filename, 'r');
    if fileID == -1
        error('Failed to open the file: %s', filename);
    end

    % Structure for storing data
    dataStruct = struct();
    currentCategory = '';    % Current category name
    currentSubcategory = ''; % Current subcategory name

    % Process the file line by line
    while ~feof(fileID)
        line = strtrim(fgetl(fileID)); % Read line and trim unnecessary spaces
        if isempty(line) || (~startsWith(line, '#') && ~startsWith(line, '*'))
            continue; % Skip empty or invalid lines
        end

        if line(1) == '#'
            % Start of a new category or subcategory
            parts = strsplit(line, ',');
            if length(parts) >= 3
                currentCategory = strtrim(parts{2});       % Category name
                currentSubcategory = strtrim(parts{3});    % Subcategory name
                % Initialize category if it does not exist
                if ~isfield(dataStruct, currentCategory)
                    dataStruct.(currentCategory) = struct();
                end
                % Initialize subcategory if it does not exist
                if ~strcmp(currentSubcategory, '_') && ...
                   ~isfield(dataStruct.(currentCategory), currentSubcategory)
                    dataStruct.(currentCategory).(currentSubcategory) = struct();
                end
            end
            continue;
        end

        if line(1) == '*'
            % Process data row
            parts = strsplit(line, ',');
            dataKey = strtrim(parts{2});  % Key of the data row (e.g., "x_m")
            subKey = strtrim(parts{3});   % Subkey of the data row (e.g., "_")
            
            if currentSubcategory == "sys_reports"
                % Process value
                value = strjoin(parts(4:end), ','); % Value starting from the fourth column
                if startsWith(value, '"') && endsWith(value, '"')
                    % Treat as a string if enclosed in quotes
                    value = value(2:end-1); % Remove quotes
                    value_list = strsplit(value, '","');
                    values = {};
                    % Loop through values
                    for i = 1:length(value_list)
                        current_value = value_list{i}; % Current element
                        try
                            % Attempt to convert to MATLAB array
                            values{end+1} = eval(current_value);
                        catch
                            % Store as string if not convertible
                            values{end+1} = current_value;
                        end
                    end
                else
                    value_list = strsplit(value, ',');
                    values = {};
                    for i = 1:length(value_list)
                        current_value = value_list{i}; % Current element
                        try
                            % Attempt to convert to MATLAB array
                            values{end+1} = eval(current_value);
                        catch
                            % Store as string if not convertible
                            values{end+1} = current_value;
                        end
                    end
                end
            else
                values = str2double(parts(4:end));  % Numeric data
            end

            if strcmp(currentSubcategory, '_')
                % If subcategory is '_', assign directly to the category
                if ~isfield(dataStruct.(currentCategory), dataKey)
                    dataStruct.(currentCategory).(dataKey) = [];
                end
                % Append data
                dataStruct.(currentCategory).(dataKey) = ...
                    [dataStruct.(currentCategory).(dataKey); values];
            else
                % Store within the subcategory
                if ~strcmp(subKey, '_')
                    % Store under subkey if it exists
                    if ~isfield(dataStruct.(currentCategory).(currentSubcategory), dataKey)
                        dataStruct.(currentCategory).(currentSubcategory).(dataKey) = struct();
                    end
                    if ~isfield(dataStruct.(currentCategory).(currentSubcategory).(dataKey), subKey)
                        dataStruct.(currentCategory).(currentSubcategory).(dataKey).(subKey) = [];
                    end
                    % Append data
                    dataStruct.(currentCategory).(currentSubcategory).(dataKey).(subKey) = ...
                        [dataStruct.(currentCategory).(currentSubcategory).(dataKey).(subKey); values];
                else
                    % Store under main key if no subkey exists
                    if ~isfield(dataStruct.(currentCategory).(currentSubcategory), dataKey)
                        dataStruct.(currentCategory).(currentSubcategory).(dataKey) = [];
                    end
                    % Append data
                    dataStruct.(currentCategory).(currentSubcategory).(dataKey) = ...
                        [dataStruct.(currentCategory).(currentSubcategory).(dataKey); values];
                end
            end
        end
    end

    % Close the file
    fclose(fileID);
end
