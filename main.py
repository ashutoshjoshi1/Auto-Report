import bz2
import pandas as pd
import matplotlib.pyplot as plt
from jinja2 import Template

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

    num_columns = len(data[0])
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

    df = pd.DataFrame([row[:max_columns] for row in data], columns=column_names[:max_columns])

    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")

    for col in df.columns:
        if col not in ["Routine Code", "Timestamp"]:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    return df

def decompress_bz2_file(file_path):
    try:
        with bz2.open(file_path, 'rb') as f:
            decompressed_content = f.read()
        return decompressed_content.decode('utf-8', errors='replace')
    except Exception as e:
        print(f"Error decompressing file: {e}")
        return ""

def main(file_path):
    decompressed_content = decompress_bz2_file(file_path)
    if decompressed_content:
        df = process_txt_file(decompressed_content)
        return df
    else:
        return "Failed to decompress and process the file."

# Load the data
data = main('/Users/ashutoshjoshi/Desktop/Github/Auto-Report/Pandora211s1_Agam_20220913_L0 (1).txt.bz2')



def plot_chart(df, title, filename):
    average_values = df.iloc[:, 25:2047].mean()
    x_values = range(len(average_values))
    
    plt.figure(figsize=(21, 9))
    plt.plot(x_values, average_values)
    plt.title(title)
    plt.xlabel('Pixel Number')
    plt.ylabel('Pixel Value')
    plt.savefig(filename)
    plt.close()

def moon_open(df):
    df1 = df[df['Routine Code'] == 'MO']
    df1 = df1.fillna(0).astype(int)
    df1 = df1.iloc[:, 999:2030]
    y = df1.mean(axis=1).tolist()
    x = range(len(y))
    plt.figure(figsize=(21, 9))
    plt.scatter(x, y)
    plt.title('Pixel Values for Moon Open')
    plt.xlabel('Pixel Number')
    plt.ylabel('Pixel Value')
    plt.savefig('moon_open.png')
    plt.close()

def sun_open(df):
    df1 = df[df['Routine Code'].isin(['SQ','SS','SO'])]
    # df1 = df1.fillna(0).astype(int)
    timest = df1.iloc[:,1]
    df1 = df1.iloc[:, 999:2030]
    y = df1.mean(axis=1).tolist()
    # x = range(len(y))
    plt.figure(figsize=(21, 9))
    plt.scatter(timest, y)
    plt.title('Pixel Values for Sun Open')
    plt.xlabel('Pixel Number')
    plt.ylabel('Pixel Value')
    plt.savefig('sun_open.png')
    plt.close()

def all_sensors(df):
    df1 = df.iloc[:, 1:2030]
    df1 = df1.fillna(0).astype(int)
    df1['Head Sensor Pressure [hPa]'] = df1['Head Sensor Pressure [hPa]'] * 0.01

    # Plotting logic
    plt.figure(figsize=(21, 9))
    plt.plot(df1['Timestamp'], df1['Electronics Temp [°C]'], label='Electronics Temp [°C]')
    plt.plot(df1['Timestamp'], df1['Control Temp [°C]'], label='Control Temp [°C]')
    plt.plot(df1['Timestamp'], df1['Aux Temp [°C]'], label='Aux Temp [°C]')
    plt.plot(df1['Timestamp'], df1['Head Sensor Temp [°C]'], label='Head Sensor Temp [°C]')
    plt.plot(df1['Timestamp'], df1['Head Sensor Humidity [%]'], label='Head Sensor Humidity [%]')

    plt.plot(df1['Timestamp'], df1['Head Sensor Pressure [hPa]'], label='Head Sensor Pressure [hPa]')

    plt.gca().xaxis.set_major_locator(plt.MaxNLocator(40))
    plt.xlabel('Timestamp')
    plt.ylabel('Measured Values')
    plt.title('Sensor Readings Over Time')
    plt.xticks(rotation=45)
    plt.legend()
    plt.savefig('all_sensor_readings.png')
    plt.close()

df_opaque = data[data['Filterwheel 2'].isin([3, 6])]
df_open = data[(data['Filterwheel 2'].isin([1, 4])) & (data['Filterwheel 1'].isin([1, 2, 4]))]
# df_moon_open = data[data['Routine Code'] == 'MO']
# df_sun_open = data[(data['Filterwheel 2'].isin([1, 2])) & (data['Routine Code'] == 'SO')]


plot_chart(df_opaque, 'Pixel Values for Opaque', 'opaque.png')
# opaque(data)
plot_chart(df_open, 'Pixel Values for Open', 'open.png')
moon_open(data)
# plot_chart(df_moon_open, 'Pixel Values for Moon Open', 'moon_open.png')
# plot_chart(df_sun_open, 'Pixel Values for Sun Open', 'sun_open.png')
sun_open(data)
# plot_chart(data, 'Pixel Values for All Sensor Readings', 'all_sensor_readings.png')
all_sensors(data)

# HTML template
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sensor Data Report</title>
    <style>
        html, body {
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(40deg, var(--color-bg1), var(--color-bg2));
            color: white;
            height: 100%;
        }

        header {
            background: rgba(0, 0, 0, 0.8);
            padding: 10px 20px;
            text-align: center;
        }

        h1, h2 {
            text-align: center;
            transition: color 0.3s;
        }

        h1:hover, h2:hover {
            color: rgba(var(--color-interactive), 1);
        }

        img {
            display: block;
            margin: 20px auto;
            width: 90%;
            box-shadow: 0 5px 15px rgba(0,0,0,0.5);
            transition: transform 0.3s ease-in-out;
        }

        img:hover {
            transform: scale(1.05);
            cursor: pointer;
        }

        :root {
            --color-bg1: rgb(108, 0, 162);
            --color-bg2: rgb(0, 17, 82);
            --color1: 18, 113, 255;
            --color2: 221, 74, 255;
            --color3: 100, 220, 255;
            --color4: 200, 50, 50;
            --color5: 180, 180, 50;
            --color-interactive: 140, 100, 255;
        }

        .gradient-bg {
            position: relative;
            overflow: hidden;
        }
    </style>
</head>
<body>
    <header>
        <h1>Sensor Data Report</h1>
    </header>

    <section class="gradient-bg">
        <h2>Opaque</h2>
        <img src="opaque.png" alt="Opaque">
        
        <h2>Open</h2>
        <img src="open.png" alt="Open">
        
        <h2>Moon Open</h2>
        <img src="moon_open.png" alt="Moon Open">
        
        <h2>Sun Open</h2>
        <img src="sun_open.png" alt="Sun Open">
        
        <h2>All Sensor Readings</h2>
        <img src="all_sensor_readings.png" alt="All Sensor Readings">
    </section>
</body>
</html>
"""

# Render HTML report
template = Template(html_template)
html_report = template.render()

# Save HTML report
with open('sensor_data_report.html', 'w') as f:
    f.write(html_report)

print("HTML report generated successfully.")
