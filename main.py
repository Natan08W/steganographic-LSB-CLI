import argparse
import sys
from steg.engine import encodeData, decodeData, getImageCapacity, StegCapacityError, StegCorruptPayloadError

def handleInfo(args):
    """Handle the 'info' command to display image capacity."""
    try:
        capacity = getImageCapacity(args.image)
        print(f"Image: {args.image}")
        print(f"Image Capacity: {capacity:,} bytes ({ capacity / 1024:.2f} KB)")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def handleEncode(args):
    """Handle the 'encode' command to embed data into an image."""
    if args.message:
        payload = args.message.encode('utf-8')
    elif args.file:
        try:
            with open(args.file, 'rb') as f:
                payload = f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            sys.exit(1)
    else:
        print("Error: Either a message or a file must be provided for encoding.")
        sys.exit(1)

    try:
        encodeData(args.input, args.output, payload, args.key or "")
        print(f"Data successfully embedded into {args.output}.")
    except StegCapacityError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

def handleDecode(args):
    """Handle the 'decode' command to extract data from an image."""
    try:
        payload = decodeData(args.input, args.key or "")
        if args.output:
            with open(args.output, 'wb') as f:
                f.write(payload)
            print(f"Data successfully extracted to {args.output}.")
        else:
            try:
                x = payload.decode('utf-8')
                print("Extracted Data (UTF-8): ")
                print(x)
            except UnicodeDecodeError:
                print("Extracted Data (binary):")
                print(payload)
    except StegCorruptPayloadError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(prog="lsb-steg", description="LSB Steganography CLI")
    subparsers = parser.add_subparsers(title="Commands", dest="command", required=True)

    # Info command
    infoParser = subparsers.add_parser("info", help="Display image capacity")
    infoParser.add_argument("image", help="Path to the image file")
    infoParser.set_defaults(func=handleInfo)

    # Encode command
    encodeParser = subparsers.add_parser("encode", help="Embed data into an image")
    encodeParser.add_argument("-i", "--input", required=True, help="Input image file path")
    encodeParser.add_argument("-o", "--output", required=True, help="Output image file path")
    encodeParser.add_argument("-m", "--message", help="Message to embed")
    encodeParser.add_argument("-f", "--file", help="File to embed")
    encodeParser.add_argument("-k", "--key", help="Encryption key (optional)")
    encodeParser.set_defaults(func=handleEncode)

    # Decode command
    decodeParser = subparsers.add_parser("decode", help="Extract data from an image")
    decodeParser.add_argument("-i", "--input", required=True, help="Input image file path")
    decodeParser.add_argument("-o", "--output", help="Output file path for extracted data (optional)")
    decodeParser.add_argument("-k", "--key", help="Decryption key (optional)")
    decodeParser.set_defaults(func=handleDecode)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)

if __name__ == "__main__":
    main()