
with open("input.txt", "r") as f:
    lines = f.readlines()
    out = '['
    for i, line in enumerate(lines):
        out += line.split(":")[0].strip() + ","
            
    print(out[:-1] + "]")