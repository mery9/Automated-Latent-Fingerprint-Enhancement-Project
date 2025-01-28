import os
from PIL import Image

def convert_png_to_500dpi(folder_path):
    if not os.path.exists(folder_path):
        print(f"The folder {folder_path} does not exist.")
        return

    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.png'):
            file_path = os.path.join(folder_path, filename)
            
            try:
                with Image.open(file_path) as img:
                    # Get and print the current DPI
                    current_dpi = img.info.get('dpi')
                    print(f"Processing {filename}")
                    print(f"Current DPI: {current_dpi}")
                    
                    if current_dpi is None:
                        print(f"Warning: {filename} does not have DPI information. Skipping this file.")
                        print("---")
                        continue
                    
                    # Calculate the new size for 500 DPI
                    width, height = img.size
                    new_width = int(width * 500 / current_dpi[0])
                    new_height = int(height * 500 / current_dpi[1])
                    
                    # Resize the image to the new dimensions
                    new_img = img.resize((new_width, new_height), Image.LANCZOS)
                    
                    # Save the new image, replacing the old one
                    new_img.save(file_path, dpi=(500, 500))
                    
                    print(f"Converted {filename} from {current_dpi} DPI to 500 DPI")
                    print(f"Original size: {width}x{height}")
                    print(f"New size: {new_width}x{new_height}")
                    print("---")
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
                print("---")

# Example usage
folder_path = '/home/chai/sourceafis-project/sourceafis-project/ProbeFingerprint_500_DPI_By_CodeConvert'
convert_png_to_500dpi(folder_path)