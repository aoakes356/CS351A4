###                                                       ###
#   Assignment 4 | by Andrew Oakes | WAH compression test   #
#                                                           #
###                                                       ###
import os   # This is imported ONLY to get file size. before and after compressions
# Did this to match the sort that seems to be done in animals_test
def sortKey(arr):
    return str(arr[0])+','+str(arr[1])+','+str(arr[2])+'\n'
# stylish method of turning each line of text text into bitmap.
#['cat','dog','turtle','bird',1-10,11-20,21-30,31-40,41-50,51-60,61-70,71-80,81-90,91-100,True, False]
#   0     1      2        3    4     5     6     7     8     9     10    11   12     13    14     15
def encode(data_points):    # takes a list, 0 being the name, 1 being the age, and 2 being true/false
    encoded = {'cat':0,'dog':0,'turtle':0,'bird':0,0:0,1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,'True':0,'False':0}
    encoded[data_points[0]] = 1
    encoded[int((int(data_points[1])-1)/10)] = 1
    encoded[data_points[2]] = 1
    return list(encoded.values())

# WAH | COMPRESS 32-BIT WORD SIZE

# General WAH algorithm
# function for getting all of the words from a column
def getWords(column, word_size):
    # Get all of the word_size-1 words, turn them into strings
    words = ([''.join(column[i*(word_size-1):(i+1)*(word_size-1)]) for i in range(0,int((len(column))/(word_size-1)))])
    # Get the last word that is sub-word_size
    words.append(''.join(column[-(len(column)%(word_size-1)):]))
    return words

def classifyWord(word, word_size):
    # Classify a word as a run of zeroes, a run of ones, or a literal.
    if(len(word) < word_size-1): # Partial word, by convention a literal.
        return 2
    count = sum([int(num) for num in word])
    if(count == word_size-1):
        return 1
    elif(count == 0):
        return 0
    else:
        return 2  

def compress(runs,ones_or_zeroes,word,word_size):
    # Generates the compressed word from the given information.
    if(runs == 0):  #literal, add header bit
        return '0'+word
    else:   # runs
        b ="{0:b}".format(runs)
        return '1'+str(ones_or_zeroes)+'0'*(word_size-2-len(b))+b

def compressCol(words,word_size):
    # State variables
    run_count = 0
    run_type = -1
    o_runs = 0
    z_runs = 0
    literals = 0
    compressed = []
    for word in words:
        res = classifyWord(word,word_size)
        if res == 0 or res == 1:   # Indicates a run.
            if res == 1:
                o_runs += 1
            elif res == 0:
                z_runs += 1
            if run_type == -1 or run_type == res:
                run_type = res
                run_count += 1
            else:   # run of a different kind
                compressed.append(compress(run_count,run_type,word, word_size))
                run_count = 1
                run_type = res
                # start new word store other one.
        else:   # literal
            literals += 1
            if run_type == -1: # no runs yet.
                compressed.append(compress(run_count,run_type,word, word_size))
                # add this word with header bit 0
            else: # currently counting runs
                compressed.append(compress(run_count,run_type,word, word_size))
                run_count = 0
                run_type = -1
                compressed.append(compress(run_count,run_type,word, word_size))
                # add current runs
                # add this word with header bit 0
    # return a tuple containing the run and literal counts
    return (compressed, z_runs,o_runs, literals)

def wah(columns, word_size):
    current = ''
    o_runs = 0
    z_runs = 0
    literals = 0
    for col in columns:
        comp = compressCol(getWords(col,word_size),word_size)
        z_runs += comp[1]
        o_runs += comp[2]
        literals += comp[3]
        current += (''.join(comp[0]))+'\n'
    return (current, z_runs, o_runs, literals)

#print(compress(7,0,'0'*31))

# Open the file that contains the data
animals_size = os.path.getsize("./animals.txt")
with open('animals.txt','r') as f:

    # split by comma, then split by new line 
    text = [line.split(',') for line in ((f.read()).split('\n')) if len(line) > 0]


# Array for storing columns of data. Will make it easier to compress later.
col = [[] for i in range(0,16)]

# Function to make a string for a given row in the column array.
rowStr = lambda columns, row: (''.join([str(columns[i][row]) for i in range(0,16)]))+'\n'

# Function to make a string for the whole column array.
wholeStr = lambda columns: ''.join([rowStr(columns,i) for i in range(0,len(columns[0]))])

# Function to add a row to the column array.
addRow = lambda columns, data: [columns[i].append(str(data[i])) for i in range(0,16)] 

# CREATE UNSORTED ANIMAL BITMAP ####

# Populate the column arrays.
[addRow(col,encode(data)) for data in text]

# CREATE SORTED ANIMAL BITMAP

# Now do it with the sorted data.
col2 = [[] for i in range(0,16)]
text.sort(key = sortKey)
[addRow(col2,encode(data)) for data in text]
o_runs = 0
z_runs = 0
literals = 0

# compress everything using the functions above, and write to the files.

# write unsorted data
with open('unsorted_bitmap_animals.txt','w') as f:
    f.write(wholeStr(col))
# Get size of the file to check compression rates.
bitmap_size = os.path.getsize("./unsorted_bitmap_animals.txt")
# write sorted data
with open('sorted_bitmap_animals.txt','w') as f:
    f.write(wholeStr(col2))
# Write sorted 32-bit word compressed data
with open('sorted_bitmap_compressed32_animals.txt','w') as f:
    res = wah(col2, 32)
    z_runs += res[1]
    o_runs += res[2]
    literals += res[3]
    f.write(res[0])
sorted_compressed_32_size = os.path.getsize("./sorted_bitmap_compressed32_animals.txt") 
print("----Sorted 32----\n0-Runs: "+str(z_runs)+"\n"+"1-Runs: "+str(o_runs)+"\n"+"Literals: "+str(literals)+"\n"+"Ratio: "+str(sorted_compressed_32_size/bitmap_size)+"\n\n")
z_runs = 0
o_runs = 0
literals = 0
# Write unsorted 32-bit word compressed data
with open('unsorted_bitmap_compressed32_animals.txt','w') as f:
    res = wah(col, 32)
    z_runs += res[1]
    o_runs += res[2]
    literals += res[3]
    f.write(res[0])

unsorted_compressed_32_size = os.path.getsize("./unsorted_bitmap_compressed32_animals.txt") 
print("----Unsorted 32----\n0-Runs: "+str(z_runs)+"\n"+"1-Runs: "+str(o_runs)+"\n"+"Literals: "+str(literals)+"\n"+"Ratio: "+str(unsorted_compressed_32_size/bitmap_size)+"\n\n")
z_runs = 0
o_runs = 0
literals = 0
# write sorted 64-bit word compressed data.
with open('sorted_bitmap_compressed64_animals.txt','w') as f:
    res = wah(col2, 64)
    z_runs += res[1]
    o_runs += res[2]
    literals += res[3]
    f.write(res[0])

sorted_compressed_64_size = os.path.getsize("sorted_bitmap_compressed64_animals.txt") 
print("----Sorted 64----\n0-Runs: "+str(z_runs)+"\n"+"1-Runs: "+str(o_runs)+"\n"+"Literals: "+str(literals)+"\n"+"Ratio: "+str(sorted_compressed_64_size/bitmap_size)+"\n\n")
o_runs = 0
z_runs = 0
literals = 0
# write unsorted 64-bit word compressed data.
with open('unsorted_bitmap_compressed64_animals.txt','w') as f:
    res = wah(col, 64)
    z_runs += res[1]
    o_runs += res[2]
    literals += res[3]
    f.write(res[0])

unsorted_compressed_64_size = os.path.getsize("unsorted_bitmap_compressed64_animals.txt") 
print("----Unsorted 64----\n0-Runs: "+str(z_runs)+"\n"+"1-Runs: "+str(o_runs)+"\n"+"Literals: "+str(literals)+"\n"+"Ratio: "+str(unsorted_compressed_64_size/bitmap_size)+"\n\n")
