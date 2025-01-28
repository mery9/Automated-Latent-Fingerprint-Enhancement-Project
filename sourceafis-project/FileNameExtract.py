from pathlib import Path

def get_existing_files(output_file):
    # Check if the output file exists and read existing file names
    output_path = Path(output_file)
    if output_path.exists():
        with output_path.open('r') as f:
            existing_files = set(f.read().splitlines())  # Read file names and store them in a set
    else:
        existing_files = set()  # Initialize an empty set if the file doesn't exist
    return existing_files

def get_files_from_path(path, output_file):
    try:
        # Get the set of existing file names
        existing_files = get_existing_files(output_file)
        
        # Open the output file in append mode
        with open(output_file, 'a') as f:
            # Create a Path object for the input path
            p = Path(path)
            
            # Iterate over files in the directory
            for file in p.iterdir():
                if file.is_file() and file.name not in existing_files:  # Avoid duplicates
                    # Write the new unique file name (including extension) to the output file
                    f.write(f"{file.name}\n")
                    existing_files.add(file.name)  # Add the file name to the set to avoid duplicates
        print(f"Unique file names have been written to {output_file}.")
    
    except Exception as e:
        print(f"Error: {e}")

# Example usage
path = "/home/chai/sourceafis-project/sourceafis-project/NIST_SD302B_V"
output_file = "FingerprintFilename.txt"
get_files_from_path(path, output_file)
