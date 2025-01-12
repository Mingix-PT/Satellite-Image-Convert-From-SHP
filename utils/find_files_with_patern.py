import os

def find_files_with_pattern(directory, pattern, count):
    matching_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.count(pattern) == count:
                matching_files.append(os.path.join(root, file))
    return matching_files

directory = 'full_cut_dataset'
pattern = 'rotated'
count = 2

matching_files = find_files_with_pattern(directory, pattern, count)
for file in matching_files:
    with open('two_rotated_files.txt', 'w') as f:
        for file in matching_files:
            f.write(file + '\n')
