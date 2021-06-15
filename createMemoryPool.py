import os
TIME_TEMPLATE ="28/08/2017"
rootDir = "C:\loggedMempoolFees" #put the loggedMempoolFees here

# Parses the data received from the Bitcoin API and returns on the relevant data 
# ID, fee, size and Dependencies

def getDependent (line):
    depend_str = line.split('{')[1].split(',')[5].split(':')[1].split('[')[1].split(']')[0]
    depend = []
    temp = depend_str.split(',')
    for parent in temp:
        if parent == "":
            break
        depend.append(parent.split('\'')[1].split('\'')[0])
    return depend


def getFee(line):
    fee_string = line.split('{')[1].split(':')[1].split('(')[1].split(')')[0][1:-1]
    if 'E' in fee_string:
        exponent = int(fee_string.split('E')[1])
        fee = 10 ** (exponent)
    else:
        fee = float(fee_string)
    return fee


def createMemoryPool(time, sample_number):  # sample_number: as we agree- you pick how many samples of the MemoryPool
    # you would like to see
    add = False
    remove = False
    day, month, year = time.split('/')

    date = year + "_" + month + "_" + day

    # utcTime = str(year) + str(month) + str(day) + "T" + str(hour[0]) + str(hour[1]) + str(hour[2])
    # dt = datetime.datetime.strptime(utcTime, "%Y%m%dT%H%M%S")
    # ut = dt.timestamp()

    memoryPool =[]


    rootDir = "C:\loggedMempoolFees" + '\\' + date


    for root, subFolders, files in os.walk(rootDir): # os.walk yields a 3-tuple (dirpath, dirnames, filenames)
        count = 0
        for currentFile in files:
            if count > sample_number:
                break
            currentFilePath = os.path.join(root, currentFile)
            reader = open(currentFilePath, 'r')
            for line in reader:
                line = line.rstrip()
                if line == "timestamp":
                    remove = False
                    if count > sample_number:
                        break
                    count+=1
                    continue
                if line == "added":
                    add = True
                    continue
                if line == "removed":
                    add = False
                    remove = True
                    continue

                if add is True:
                    memoryPool.append([line.split('{')[0], getDependent(line), getFee(line),
                                       int(line.split('{')[1].split(',')[-1].split(':')[1][1:-1])])
                if remove is True:
                    element = [line.split('{')[0], getDependent(line), getFee(line),
                                       line.split('{')[1].split(',')[-1].split(':')[1][1:-1]]
                    if element in memoryPool:
                        memoryPool.remove(element)

    return memoryPool
