import hashlib

def sha256encrypt(hash_string):
    encryptedPassword = hashlib.sha256(hash_string.encode()).hexdigest()
    return encryptedPassword

#userID is just a sha256 hash of email + password
def generate_uuid(userDict):
    return sha256encrypt(userDict["email"]+userDict["password"]);


def generate_email_and_password_hash(email, password):
	return sha256encrypt(email+password);
