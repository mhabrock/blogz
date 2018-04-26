def valid_input(input):
    
    if len(input) < 0 and (len(input) < 3 or len(input) > 40):
        return False
    for x in input:
        if x == " ":
            return False
    
    return True

def verify_pass(pass1, pass2):
    
    if pass2 == pass1:
        return True
    else:
        return False
    