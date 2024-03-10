import os
import pydicom

def load_ct_exam(folder_path):
    # Initialize an empty list to store the loaded DICOM files
    dicom_files = []

    # Iterate over the files in the specified folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        try:
            # Load the DICOM file using pydicom
            dicom_file = pydicom.dcmread(file_path)
            
            # Append the loaded DICOM file to the list
            dicom_files.append(dicom_file)
        except pydicom.errors.InvalidDicomError:
            # Skip the file if it is not a valid DICOM file
            continue
        except Exception as e:
            print(f"Error loading file {file_path}: {str(e)}")

    return dicom_files