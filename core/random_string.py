# Generate random string
# - Used to generate API token

import random



def generate_token():
    # TOKEN SETTINGS
    LENGHT = 16

    CHARACTERS = "!$%&\()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~"

    token = ""
    
    for i in range(LENGHT):
        token += CHARACTERS[random.randrange(0, len(CHARACTERS))]

    return token
