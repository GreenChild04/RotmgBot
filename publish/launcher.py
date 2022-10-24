import base64, pickle, os, time, socket;
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import engine;
from getmac import get_mac_address as gma
from engine import Error;


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
            raise Error("Encryption", "Engine could not be decrypted");

        if not isByte:
            return decrypted.decode()
        else:
            return decrypted


if __name__ == "__main__":
    '''Launching Engine'''

    startTime = time.time();

    os.system("cls" if os.name == "nt" else "clear");
    print(
    f"""*Green & Crow's ROTMG bot*

    {time.time() - startTime}: Attempting to launch bot"""
    );

    try:
        encryption = Encryption();

        def getPasscode():
            passcode_decoded = base64.b85decode(b'M{;FlZYD!=Z+BlwZbW5vP+@a(V{c?-');
            print(passcode_decoded.decode());
            return passcode_decoded.decode();

        def getPassword():
            ip = gma();
            key = getPasscode();
            print(f"{ip}`{key}");
            return f"{ip}`{key}";

        try: decoded = base64.b85decode(open("Engine.rot", "rb").read());
        except: raise Error("B64", "Engine file not found");

        decrypt = encryption.decryptData(
            getPassword(),
            decoded,
            True,
        );

        try: engine = pickle.loads(decrypt);
        except Exception as error: raise Error(f"Pickle", "Engine Object Broken; Python Error {[error]}");
        engine.run();

    except Exception as error:
        print(f"{time.time() - startTime}: Failed to launch bot (ErrorCode: {error})");
