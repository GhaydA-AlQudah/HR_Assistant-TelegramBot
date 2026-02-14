from pwdlib import PasswordHash
password_hash = PasswordHash.recommended()
print(password_hash.hash("1234gh"))
