InputType = input("Please enter 'Light' or 'Sound': \n").lower()
if InputType == "sound":
    print("Would you like to do close range or long range(experimental)?")
    SoundType = input("Please enter sr or lr: \n").lower()
    if SoundType == "lr":
        exec(open("./test.py").read())
    elif SoundType == "sr":
        exec(open("./SoundToMorse.py").read())
    else:
        print("Invalid Input!")
elif InputType == "light":
    exec(open("./LightMaxMin.py").read())

