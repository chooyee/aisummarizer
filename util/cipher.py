from cryptography.fernet import Fernet
from pylogger import LogUtility
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import sys

const_key = b"V2hlbnlvdWRvdGhpbmdzZnJvbXlvdXJzb3VsLHlvdWZlZWxhcml2ZXJtb3ZpbmdpbnlvdSxham95"

class Cipher:
    def __init__(self, password):

        salt_key = b"3f5e8a7c9b2d4e1f"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt_key,
            iterations=100000
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        self.logger = LogUtility.get_logger("cipher")
        self.fernet = Fernet(key)

    @staticmethod
    def GenerateKey():
        return Fernet.generate_key()

    def Encrypt(self, message):
        try:
            encMessage = self.fernet.encrypt(message.encode())
            return encMessage
        except Exception as e:
            self.logger.error(f'{sys._getframe().f_code.co_name}: {e}')
            raise

    def Decrypt(self, encMessage):
        try:
            decMessage = self.fernet.decrypt(encMessage).decode()
            return decMessage
        except Exception as e:
            self.logger.error(f'{sys._getframe().f_code.co_name}: {e}')
            raise

    @staticmethod
    def EncryptStr(message):
        cipher = Cipher(const_key)
        secret = cipher.Encrypt(message)
        return secret.decode('ascii')
        
    @staticmethod
    def DecryptStr(secret):
        cipher = Cipher(const_key)        
        return cipher.Decrypt(secret)
    
    # @staticmethod
    # def EncryptStr(message, returnType: Literal['base64', 'plain'] = 'base64'):
    #     cipher = Cipher(const_key)
    #     secret = cipher.Encrypt(message)
    #     if returnType=='base64':
    #         return EncodeBase64(secret)
    #     else:
    #         return secret
        
    # @staticmethod
    # def DecryptStr(secret, msgType: Literal['base64', 'plain'] = 'base64'):
    #     cipher = Cipher(const_key)        
    #     if msgType=='base64':
    #         secretStr = DecodeBase64(secret)
    #     else:
    #         secretStr = secret
    #     return cipher.Decrypt(secretStr)
    
if __name__ == "__main__":
    action = input("What do you want to do? 1 for [Encrypt], 2 for [Decrypt], 3 for [Exit]")
    match action:
        case "1":
            secret = input("Enter string to encrypt")
            logger = LogUtility.get_logger("cipher")
            logger.debug(Cipher.EncryptStr(secret))
            print(Cipher.EncryptStr(secret))
        case "2":
            secret = input("Enter secret to decrypt")
            print(Cipher.DecryptStr(secret))