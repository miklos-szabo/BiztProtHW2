from Crypto.Hash import SHA256

USERS = {
    'admin': 'adm1n',
    'user': 'usr1'
}


def write(database):
    with open('users.txt', 'w') as f:
        for k, v in database.items():
            hk = SHA256.new(k.encode('ascii')).hexdigest()
            vk = SHA256.new(v.encode('ascii')).hexdigest()
            line = f"{hk} {vk}\n"
            f.write(line)


write(USERS)