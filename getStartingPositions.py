def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output',
                        help="output prefix")
    args = parser.parse_args()

    positions = getStartingPositions(args.output)
    outfile = args.output+".startPositions.pkl"
    storePositions(positions,outfile)

# -------------------------------------------------------------------------------

def getStartingPositions(prefix):
    positions = dict()
    with open(prefix+".toxin.faa") as t, open(prefix+".antitoxin.faa") as a:
        for line in t:
            if line.startswith(">"):
                name,start = getInfoFromHeader(line)
                positions[name] = start

        for line in a:
            if line.startswith(">"):
                name,start = getInfoFromHeader(line)
                positions[name] = start

    return positions

def getInfoFromHeader(header):
    header = header.strip().split()
    name = header[0].split("|")[1]
    start = header[1].split(":")[1].split("..")[0]
    return name,int(start)

def storePositions(positions,outfile):
    import cPickle as pickle
    with open(outfile,'wb') as out:
        pickle.dump(positions,out)

# -------------------------------------------------------------------------------

if __name__ == '__main__':
    main()
