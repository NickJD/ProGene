import collections

from ORForise.utils import revCompIterative
from ORForise.utils import sortORFs

def FGENESB(genome_to_compare,parameters,genome):
    FGENESB_ORFs = collections.OrderedDict()
    genome_Size = len(genome)
    genome_rev = revCompIterative(genome)
    with open('Tools/FGENESB/FGENESB_'+genome_to_compare+'_'+parameters+'.txt','r') as FGENESB_input:
        for line in FGENESB_input:
            if '>GENE' in line:
                line = line.split()
                if '2208' in line:
                    print("ss")
                if len(line) == 10 and ">GENE" in line[0]:
                    start = int(line[2])
                    stop = int(line[4])
                    strand = line[9]
                    if '-' in strand:  # Reverse Compliment starts and stops adjusted
                        r_start = genome_Size - stop
                        r_stop = genome_Size - start
                        startCodon = genome_rev[r_start:r_start + 3]
                        stopCodon = genome_rev[r_stop - 2:r_stop + 1]
                    elif '+' in strand:
                        startCodon = genome[start - 1:start+2]
                        stopCodon = genome[stop - 3:stop]
                    po = str(start) + ',' + str(stop)
                    orf = [strand, startCodon, stopCodon]
                    FGENESB_ORFs.update({po: orf})

    FGENESB_ORFs = sortORFs(FGENESB_ORFs)
    return FGENESB_ORFs

































