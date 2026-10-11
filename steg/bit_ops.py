from typing import List, Generator

def embedBit(channelByte: int, bit: int) -> int:
    # Embed a single bit into the least significant bit of a channel byte.
    return (channelByte & 0xFE) | (bit & 1)

def extractBit(channelByte: int) -> int:
    # Extract the least significant bit from a channel byte.
    return channelByte & 1

def bytesToBits(data: bytes) -> Generator[int, None, None]:
    # Convert bytes to a generator of bits. Each byte is converted to 8 bits, starting from the most significant bit.
    for byte in data:
        for i in range(8):
            yield (byte >> (7 - i)) & 1

def bitsToBytes(bits: List[int]) -> bytes:
    # Convert a list of bits to bytes. The length of the bits list must be a multiple of 8.
    if len(bits) % 8 != 0:
        raise ValueError("Number of bits must be a multiple of 8.")

    out = bytearray()
    for i in range(0, len(bits), 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | bits[i + j]
        out.append(byte)
    return bytes(out)