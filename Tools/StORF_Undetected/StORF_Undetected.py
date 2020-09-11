import collections

from ..utils import revCompIterative


def StORF_Undetected(tool,genome):
    storf_orfs = collections.OrderedDict()
    genome_Size = len(genome)
    genome_Rev = revCompIterative(genome)
    with open('Tools/StORF_Undetected/'+tool,'r') as storf_input:
        for line in storf_input:
            line = line.split()
            if "StORF" in line[1] and "ORF" in line[2]:
                start = int(line[3])
                stop = int(line[4])
                strand = line[6]
                if '-' in strand:  # Reverse Compliment starts and stops adjusted
                    r_start = genome_Size - stop
                    r_stop = genome_Size - start
                    startCodon = genome_Rev[r_start:r_start + 3]
                    stopCodon = genome_Rev[r_stop - 2:r_stop + 1]
                elif '+' in strand:
                    startCodon = genome[start - 1:start -1 + 3]
                    stopCodon = genome[stop - 3:stop -1 + 1]
                po = str(start) + ',' + str(stop)
                orf = [strand, startCodon, stopCodon]
                storf_orfs.update({po:orf})
    return storf_orfs








