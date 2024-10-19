import tiktoken

def GetNumOfTokens(text):
    enc = tiktoken.get_encoding("o200k_base")
    tokens = enc.encode(text)
    return len(tokens)