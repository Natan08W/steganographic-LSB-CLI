import struct
from PIL import Image
from steg.bit_ops import embedBit, extractBit, bytesToBits, bitsToBytes
from steg.crypto import xorCrypto

magicBytes = b'STEG'  # Magic bytes to identify the presence of hidden data
headerFormat = '>4sIB'  # Struct format for the header: magic bytes, data length (unsigned int), and encryption flag (unsigned char)
headerSize = struct.calcsize(headerFormat)  # Calculate the size of the header based on the struct format

flagUnencrypted = 0x00  # Flag indicating that the data is unencrypted
flagEncrypted = 0x01  # Flag indicating that the data is encrypted

class StegCapacityError(Exception):
    """Custom exception for steganography capacity errors."""
    pass

class StegCorruptPayloadError(Exception):
    """Custom exception for corrupted payload errors."""
    pass

def getImageCapacity(imagePath: str) -> int:
    """Calculate the maximum number of bytes that can be hidden in the given image."""
    with Image.open(imagePath) as img:
        img = img.convert('RGB')  # Ensure the image is in RGB mode
        totalChannels = img.width * img.height * 3  # Each pixel has 3 channels (R, G, B)
        maxBytes = (totalChannels // 8) - headerSize  # Each byte requires 8 bits, so divide by 8 to get the maximum number of bytes
        width, height = img.size
        # Each pixel can hide 3 bits (one in each RGB channel), so the capacity in bytes is (width * height * 3) // 8
        return max(0, maxBytes)

def encodeData(
        inputImagePath: str,
        outputImagePath: str,
        payload: bytes,
        key: str = ""
 ) -> None:
    """Embed the payload into the input image and save it as the output image."""
    if key:
        payload = xorCrypto(payload, key)  # Encrypt the payload if a key is provided
        encryptionFlag = flagEncrypted
    else:
        encryptionFlag = flagUnencrypted

    payloadLength = len(payload)
    header = struct.pack(headerFormat, magicBytes, payloadLength, encryptionFlag)  # Create the header with magic bytes, payload length, and encryption flag
    envelope = header + payload  # Combine the header and payload
    envelopeLength = list(bytesToBits(envelope))  # Convert the envelope to a list of bits
    totalBits = len(envelopeLength)  # Total number of bits to embed
    with Image.open(inputImagePath) as img:
        img = img.convert('RGB')  # Ensure the image is in RGB mode
        pixelBytes = bytearray(img.tobytes())  # Get the raw pixel data as bytes

        if totalBits > len(pixelBytes):
            raise StegCapacityError("The image does not have enough capacity to hold the data.")

        for i, bit in enumerate(envelopeLength):
            pixelBytes[i] = embedBit(pixelBytes[i], bit)  # Embed each bit into the corresponding pixel byte

        encodedImage = Image.frombytes('RGB', img.size, bytes(pixelBytes))  # Create a new image from the modified pixel bytes
        encodedImage.save(outputImagePath, format = "PNG")  # Save the encoded image to the specified output path

def decodeData(inputImagePath: str, key: str = "") -> bytes:
    """Extract the hidden payload from the input image."""
    with Image.open(inputImagePath) as img:
        img = img.convert('RGB')  # Ensure the image is in RGB mode
        pixelBytes = bytearray(img.tobytes())  # Get the raw pixel data as bytes

        # Extract the header bits from the pixel bytes
        headerBitsNeeded = headerSize * 8
        if len(pixelBytes) < headerBitsNeeded:
            raise StegCorruptPayloadError("The image does not contain enough data to extract the header.")

        rawHeaderBits = [extractBit(pixelBytes[i]) for i in range(headerBitsNeeded)]  # Extract the header bits from the pixel bytes
        headerBytes = bitsToBytes(rawHeaderBits)  # Convert the header bits back to bytes

        # Unpack the header to retrieve magic bytes, payload length, and encryption flag
        magic, payloadLength, encryptionFlag = struct.unpack(headerFormat, headerBytes)

        if magic != magicBytes:
            raise StegCorruptPayloadError("The image does not contain valid steganographic data.")

        # Extract the payload bits based on the payload length
        payloadBitsNeeded = headerBitsNeeded + (payloadLength * 8)
        if len(pixelBytes) < payloadBitsNeeded:
            raise StegCorruptPayloadError("The image does not contain enough data to extract the payload.")

        rawPayloadBits = [extractBit(pixelBytes[i]) for i in range(headerBitsNeeded, payloadBitsNeeded)]
        rawPayload = bitsToBytes(rawPayloadBits)  # ✅ Convert list of bits back to bytes

        if encryptionFlag == flagEncrypted:
            if not key:
                raise ValueError("A key is required to decrypt the data.")
            return xorCrypto(rawPayload, key)

        return rawPayload