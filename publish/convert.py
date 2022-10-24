import base64, socket;
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from getmac import get_mac_address as gma


'''Passcodes for versions'''
["Indev"] and "Green&Crow_InDevPasscode";


class Encryption:
    def getKeyFromCustomPass(self, password_provided):
        try:
            password = password_provided.encode()
        except:
            password = password_provided

        salt = b'h\x1e^\xed\n\xb9>\x16(v\x89\x82HW\xa1V'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key


    def encryptData(self, msg, passwordProv, isByte=False):
        if not isByte:
            try:
                encoded = str(msg).encode()
            except:
                encoded = msg
        else:
            encoded = msg

        f = Fernet(self.getKeyFromCustomPass(passwordProv))
        encrypted = f.encrypt(encoded)
        return encrypted


    def decryptData(self, passwordProv, encrypted, isByte=False):
        if encrypted[0] == 'b':
            new_encrypted = encrypted[1:]
            new_encrypted = new_encrypted.replace("'", '')
            new_encrypted = new_encrypted.strip('"')
            new_encrypted = new_encrypted.encode()
        else:
            try:
                new_encrypted = encrypted.encode()
            except:
                new_encrypted = encrypted

        f = Fernet(self.getKeyFromCustomPass(passwordProv))

        try:
            decrypted = f.decrypt(new_encrypted)
        except:
            print("\nERROR: ENCRYPTION PASSWORD NOT CORRECT\n")

        if not isByte:
            return decrypted.decode()
        else:
            return decrypted


'''Converstion'''

print("*GC's Engine Conversion Tool*\nWelcome nerd, this is GC's way to prevent piracy!");

encryption = Encryption();

def getPass():
    # ip = input("User's Local Ip: ");
    ip = gma();
    passcode = input("User's Passcode: ");
    return f"{ip}`{passcode}";

og = open(input("File Location: "), "rb").read();

encrypted = Encryption().encryptData(og, getPass(), True);

encoded = base64.b85encode(encrypted);

open("Engine.rot", "w+").write(encoded.decode());

print("Done");
