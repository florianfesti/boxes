def inplace_change(filename, old_string, new_string):
    # Safely read the input filename using 'with'
    with open(filename) as f:
        newText=f.read().replace(old_string, new_string)
    with open(filename, "w") as f:
        f.write(newText)
	
import glob

for fi in glob.glob("../inkex/*.inx"):
    inplace_change(fi, ">boxes</co", ">boxes.exe</co")  
