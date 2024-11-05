import argparse
from PIL import Image
import exifread
import binascii
import re

def extract_gps_info(image_path):
    try:
        with open(image_path, 'rb') as f:
            tags = exifread.process_file(f)
        if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
            latitude = tags['GPS GPSLatitude']
            latitude_ref = tags['GPS GPSLatitudeRef']
            longitude = tags['GPS GPSLongitude']
            longitude_ref = tags['GPS GPSLongitudeRef']
            lat = convert_to_degrees(latitude)
            if latitude_ref.values != 'N':
                lat = -lat
            lon = convert_to_degrees(longitude)
            if longitude_ref.values != 'E':
                lon = -lon
            lat = round(lat, 3)
            lon = round(lon, 3)
            return lat, lon
        else:
            return None
    except Exception as e:
        print(f"Error extracting GPS info: {e}")
        return None

def convert_to_degrees(value):
    d = float(value.values[0].num) / float(value.values[0].den)
    m = float(value.values[1].num) / float(value.values[1].den)
    s = float(value.values[2].num) / float(value.values[2].den)
    return d + (m / 60.0) + (s / 3600.0)

def check_image_validity(image_path):
    try:
        with Image.open(image_path) as img:
            img.verify()
        return True
    except (IOError, SyntaxError) as e:
        print(f"Invalid image file: {e}")
        return False

def read_and_convert_to_ascii(file_path):
    with open(file_path, 'rb') as file:
        binary_content = file.read()
    hex_content = binascii.hexlify(binary_content).decode('utf-8')
    return ''.join(chr(int(hex_content[i:i+2], 16)) for i in range(0, len(hex_content), 2) if 32 <= int(hex_content[i:i+2], 16) <= 126)

def extract_pgp_key(ascii_string):
    match = re.search(r'-----BEGIN PGP PUBLIC KEY BLOCK-----(.*?)-----END PGP PUBLIC KEY BLOCK-----', ascii_string, re.DOTALL)
    return match.group(1).strip() if match else None

def print_pgp_key(file_path):
    ascii_content = read_and_convert_to_ascii(file_path)
    pgp_key = extract_pgp_key(ascii_content)
    if pgp_key:
        formatted_key = "\n".join(pgp_key.split())
        print(f"-----BEGIN PGP PUBLIC KEY BLOCK-----\n{formatted_key}\n-----END PGP PUBLIC KEY BLOCK-----")
    else:
        print("No PGP key found in the provided file.")

def main():
    parser = argparse.ArgumentParser(description='Process some flags.')
    parser.add_argument('-map', type=str, help='Path to the image for extracting location')
    parser.add_argument('-steg', type=str, help='Path to the image for extracting hidden PGP key')
    args = parser.parse_args()

    if args.map:
        if check_image_validity(args.map):
            location = extract_gps_info(args.map)
            if location:
                print(f"Lat/Lon:\t({location[0]}) / ({location[1]})")
            else:
                print("No GPS EXIF data found.")
        else:
            print("Invalid image file.")

    if args.steg:
        if check_image_validity(args.steg):
            print_pgp_key(args.steg)
        else:
            print("Invalid image file.")

if __name__ == "__main__":
    main()
