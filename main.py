import bz2
import pandas as pd

def process_txt_file(file_content):
    lines = file_content.split('\n')
    data = []
    section = 0

    for line in lines:
        line = line.strip()
        if section == 0 and line.startswith("----------"):
            section = 1
        elif section == 1 and line.startswith("----------"):
            section = 2
        elif section == 2 and not line.startswith("#") and "INFO" not in line and line.strip():
            data.append(line.split())

    if not data:
        return pd.DataFrame()

    if data:
        num_columns = len(data[0])
    else:
        return pd.DataFrame()

    max_columns = 2076
    base_columns = [
        "Routine Code", "Timestamp", "Routine Count", "Repetition Count",
        "Duration", "Integration Time [ms]", "Number of Cycles", "Saturation Index",
        "Filterwheel 1", "Filterwheel 2", "Zenith Angle [deg]", "Zenith Mode",
        "Azimuth Angle [deg]", "Azimuth Mode", "Processing Index", "Target Distance [m]",
        "Electronics Temp [°C]", "Control Temp [°C]", "Aux Temp [°C]", "Head Sensor Temp [°C]",
        "Head Sensor Humidity [%]", "Head Sensor Pressure [hPa]", "Scale Factor", "Uncertainty Indicator"
    ]

    num_base_columns = len(base_columns)
    num_pixel_columns = min(num_columns, max_columns) - num_base_columns

    pixel_columns = [f"Pixel_{i+1}" for i in range(num_pixel_columns)]
    column_names = base_columns + pixel_columns

    # Convert to DataFrame
    df = pd.DataFrame([row[:max_columns] for row in data], columns=column_names[:max_columns])
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")

    return df

def decompress_bz2_file(file_path):
    try:
        with bz2.open(file_path, 'rb') as f:  # Open as binary
            decompressed_content = f.read()
        return decompressed_content.decode('utf-8', errors='replace')  # Use 'replace' to handle undecodable bytes
    except Exception as e:
        print(f"Error decompressing file: {e}")
        return ""

def main():
    file_path = "/Users/ashutoshjoshi/Desktop/Github/Auto-Report/Pandora211s1_Agam_20240520_L0.txt.bz2"
    decompressed_content = decompress_bz2_file(file_path)
    if decompressed_content:
        df = process_txt_file(decompressed_content)
        print(df)
    else:
        print("Failed to decompress and process the file.")

if __name__ == "__main__":
    main()
