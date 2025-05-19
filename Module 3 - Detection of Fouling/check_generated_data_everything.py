import csv

# --- Configuration ---
# IMPORTANT: Change this to the actual path of your CSV file if different
CSV_FILEPATH = 'generated_data_everything/fouling_iou_results.csv'
FILENAME_HEADER = 'Filename'  # The header for the filename column
TARGET_IOU_HEADER = 'IoU_5'   # The specific IoU column to sort by
# -------------------

results_list = []

try:
    with open(CSV_FILEPATH, mode='r', newline='') as infile:
        reader = csv.DictReader(infile)
        
        # Check if the required headers are present
        if FILENAME_HEADER not in reader.fieldnames:
            print(f"Error: Filename header '{FILENAME_HEADER}' not found in CSV file '{CSV_FILEPATH}'.")
            print(f"Available headers: {reader.fieldnames}")
            exit()
        if TARGET_IOU_HEADER not in reader.fieldnames:
            print(f"Error: Target IoU header '{TARGET_IOU_HEADER}' not found in CSV file '{CSV_FILEPATH}'.")
            print(f"Available headers: {reader.fieldnames}")
            exit()

        for row_number, row_data in enumerate(reader, 1):
            filename = row_data.get(FILENAME_HEADER)
            iou_value_str = row_data.get(TARGET_IOU_HEADER)

            if filename is None or filename.strip() == "":
                print(f"Warning: Row {row_number} has missing or empty filename. Skipping.")
                continue

            if iou_value_str is None or iou_value_str.strip() == "":
                print(f"Warning: Row {row_number} for filename '{filename}' has missing or empty value for '{TARGET_IOU_HEADER}'. Skipping.")
                continue

            try:
                iou_value_float = float(iou_value_str)
                results_list.append({'filename': filename, 'value': iou_value_float})
            except ValueError:
                print(f"Warning: Row {row_number} for filename '{filename}' has a non-numeric value ('{iou_value_str}') in '{TARGET_IOU_HEADER}'. Skipping.")
                continue

    if not results_list:
        print(f"No data found for '{TARGET_IOU_HEADER}' or filenames in '{CSV_FILEPATH}'.")
    else:
        # Sort the list by 'value' (which is the TARGET_IOU_HEADER score) in descending order
        results_list.sort(key=lambda item: item['value'], reverse=True)
        
        print(f"\n--- Filenames sorted by '{TARGET_IOU_HEADER}' (Highest to Lowest) ---")
        
        header_filename_text = FILENAME_HEADER
        header_value_text = f"{TARGET_IOU_HEADER} Value"
        
        # Determine column width for filename for cleaner printing
        max_len_filename = max(len(item['filename']) for item in results_list) if results_list else 0
        max_len_filename = max(max_len_filename, len(header_filename_text))  # Ensure header fits

        print(f"{header_filename_text:<{max_len_filename}}  {header_value_text}")
        print(f"{'-'*max_len_filename}  {'-'*len(header_value_text)}")
        for item in results_list:
            print(f"{item['filename']:<{max_len_filename}}  {item['value']:.4f}")

except FileNotFoundError:
    print(f"Error: The CSV file '{CSV_FILEPATH}' was not found. Please check the path.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")