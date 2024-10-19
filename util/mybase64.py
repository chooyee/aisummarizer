import base64

def EncodeBase64(string):
    base64_bytes = base64.b64encode(string.encode("ascii"))
    #print(f"Encoded string: {base64_string}")
    return base64_bytes.decode("ascii")

def DecodeBase64(base64_string):
    # Decode the Base64 string back to the original string
    string_bytes = base64.b64decode(base64_string.encode("ascii"))
    # sample_string = string_bytes.decode("ascii")
    # print(f"Decoded string: {sample_string}")
    return string_bytes.decode("ascii")