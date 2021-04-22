import argparse
import ProGene.Tools.utils as utils
import collections
import numpy as np
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-r', '--results', required=True, help='Which output to look at?')
parser.add_argument('-a', '--annotation', required=True, help='Genome Annotation File')

args = parser.parse_args()


def gc_count(dna):
    c = 0
    a = 0
    g = 0
    t = 0
    n = 0
    for i in dna:
        if "C" in i:
            c += 1
        elif "G" in i:
            g += 1
        elif "A" in i:
            a += 1
        elif "T" in i:
            t+=1
        elif "N" in i:
            n+=1
    gc_content = format((g + c) * 100 / (a + t + g + c + n),'.2f')
    #n_per = n * 100 / (a + t + g + c + n)
    return gc_content

def revCompIterative(watson):
    complements = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C', 'N': 'N'}
    watson = watson.upper()
    watsonrev = watson[::-1]
    crick = ""
    for nt in watsonrev:
        crick += complements[nt]
    return crick

def start_Codon_Count(starts,lengths):
    try:
        atg_P = format(100 * starts['ATG'] / len(lengths), '.2f')
        gtg_P = format(100 * starts['GTG'] / len(lengths), '.2f')
        ttg_P = format(100 * starts['TTG'] / len(lengths), '.2f')
        att_P = format(100 * starts['ATT'] / len(lengths), '.2f')
        ctg_P = format(100 * starts['CTG'] / len(lengths), '.2f')
    except ZeroDivisionError:
        atg_P,gtg_P,ttg_P,att_P,ctg_P = 0,0,0,0,0
    return atg_P,gtg_P,ttg_P,att_P,ctg_P#,other_Start_P,other_Starts

def stop_Codon_Count(stops,lengths):
    try:
        tag_P = format(100 * stops['TAG'] / len(lengths), '.2f')
        taa_P = format(100 * stops['TAA'] / len(lengths), '.2f')
        tga_P = format(100 * stops['TGA'] / len(lengths), '.2f')
    #return atg_P, gtg_P, ttg_P, att_P, ctg_P  # ,other_Start_P,other_Starts
    except ZeroDivisionError:
        tag_P,taa_P,tga_P = 0,0,0
    return tag_P,taa_P,tga_P#,other_Stop_P,other_Stops

def partial_gene_read(results,partial_genes):
    #partial Genes Read-In
    orf_Lengths = []
    gene_Lengths = []
    results_in = open('../Tools/'+results)
    read = False
    prev = ''
    for line in results_in:
        line = line.strip()
        if read == True:
            if line.startswith('Gene:'):
                line = line.replace('Gene:','')
                entry = line.split('_')
                g_Pos = entry[0]+'_'+entry[1]
                strand = entry[2]
                prev = 'Gene'
            elif line.startswith('ORF:'):
                line = line.replace('ORF:', '')
                entry = line.split('_')
                o_Pos = entry[0] + '_' + entry[1]
                prev = 'ORF'
            elif line:
                if 'Gene' in prev:
                    g_Seq = line.strip()
                    gene_Lengths.append(len(g_Seq))
                elif 'ORF' in prev:
                    o_Seq = line.strip()
                    orf_Lengths.append(len(o_Seq))
            elif not line:
                g_GC = gc_count(g_Seq)
                o_GC = gc_count(o_Seq)
                partial_genes.update({g_Pos:[strand,g_Seq,g_GC,o_Pos,o_Seq,o_GC]})
        if line.startswith('Partial_Gene_Hits:'):
            read = True

    return partial_genes,orf_Lengths,gene_Lengths


def detail_transfer(genes,partial_genes):
    for partial,m_details in partial_genes.items():
        try:
            details = genes[partial]
            gc = details[2]
            up_Overlap = details[3]
            down_Overlap = details[4]
            m_details.insert(2,gc)
            m_details.insert(3,up_Overlap)
            m_details.insert(4,down_Overlap)
        except KeyError:
            pass
    return partial_genes


def result_compare(results,annotation):
    genome = ""
    with open('../Genomes/' + annotation + '.fa', 'r') as genome_file:
        for line in genome_file:
            line = line.replace("\n", "")
            if ">" not in line:
                genome += str(line)

    partial_genes = collections.OrderedDict()
    partial_genes,orf_Lengths,gene_Lengths = partial_gene_read(results,partial_genes)
#    genes = read_original_annotation(gff)
    #Analysis

    # genome_Rev = revCompIterative(genome)
    # genome_Size = len(genome)
    # genes = collections.OrderedDict()
    # lengths_PCG = []
    # gene_Overlaps = []
    # count = 0
    # prev_Stop = 0
    # strands = collections.defaultdict(int)
    # short_PCGs = []
    # pcg_GC = []
    # with open('../Genomes/' + annotation + '.gff', 'r') as genome_gff:
    #     for line in genome_gff:
    #         line = line.split('\t')
    #         try:
    #             if "CDS" in line[2] and len(line) == 9:
    #                 start = int(line[3])
    #                 stop = int(line[4])
    #                 strand = line[6]
    #                 strands[strand] += 1
    #                 gene = str(start) + ',' + str(stop) + ',' + strand
    #                 if strand == '-':
    #                     r_Start = genome_Size - stop
    #                     r_Stop = genome_Size - start
    #                     seq = (genome_Rev[r_Start:r_Stop + 1])
    #                 elif strand == '+':
    #                     seq = (genome[start - 1:stop])
    #                 startCodon = seq[0:3]
    #                 stopCodon = seq[-3:]
    #                 length = stop - start
    #                 if length < utils.SHORT_ORF_LENGTH:
    #                     short_PCGs.append(gene)
    #                     #print(line)
    #                 n_per, gc = gc_count(seq)
    #                 pcg_GC.append(float(gc))
    #                 lengths_PCG.append(length)
    #                 if prev_Stop > start:
    #                     overlap = prev_Stop - start
    #                     gene_Overlaps.append(overlap)
    #                 else:
    #                     overlap = 0
    #                 count += 1
    #                 prev_Stop = stop
    #                 pos = str(start)+'_'+str(stop)
    #
    #                 if genes:
    #                     prev_details = genes[prev_pos]
    #                     prev_details.insert(4,overlap)
    #                     genes.update({prev_pos:prev_details})
    #                 genes.update({pos:[strand,length,gc,overlap,seq,startCodon,stopCodon]})
    #                 prev_pos = pos
    #
    #
    #
    #         except IndexError:
    #             continue

    orf_Median = np.median(orf_Lengths)
    gene_Median = np.median(gene_Lengths)
    strands = collections.defaultdict(int, {'-': 0, '+': 0})
    # Hard coded codons - Not ideal
    gene_Starts = collections.OrderedDict({'ATG':0,'ATT':0,'CTG':0,'GAC':0,'GTG':0,'TTG':0})
    gene_Stops = collections.OrderedDict({'TAA':0,'TAG':0,'TGA':0})
    gene_GC = []
    orf_Starts = collections.OrderedDict({'ATG':0,'ATT':0,'CTG':0,'GAC':0,'GTG':0,'TTG':0})
    orf_Stops = collections.OrderedDict({'TAA':0,'TAG':0,'TGA':0})
    orf_GC = []

    for gene, data in partial_genes.items():
        print(data)
        strands[data[0]] +=1
        try:
            gene_Starts[data[1][0:3]] +=1
            gene_Stops[data[1][-3:]] +=1
            gene_GC.append(float(data[2]))
            orf_Starts[data[4][0:3]] +=1
            orf_Stops[data[4][-3:]] +=1
            orf_GC.append(float(data[5]))
        except KeyError:
            sys.exit(data)

    gene_Median_GC = np.median(gene_GC)
    orf_Median_GC = np.median(orf_GC)
    # atg_P = format(100* gene_Starts['ATG'] / len(gene_Lengths),'.2f')
    # gtg_P = format(100 * gene_Starts['GTG'] / len(gene_Lengths),'.2f')
    # ttg_P = format(100 * gene_Starts['TTG'] / len(gene_Lengths),'.2f')
    # att_P = format(100 * gene_Starts['ATT']  / len(gene_Lengths),'.2f')
    # ctg_P = format(100 * gene_Starts['CTG']  / len(gene_Lengths),'.2f')
    # #other_Start_P = format(100 * other / len(gene_Lengths),'.2f')
    #
    # orf_GC_Median = format(np.median(pcg_GC),'.2f')
    # num_Short_PCGs = len(short_PCGs)
    #
    # partial_genes = detail_transfer(genes,partial_genes)

    g_atg_P, g_gtg_P, g_ttg_P, g_att_P, g_ctg_P = start_Codon_Count(gene_Starts,gene_Lengths)
    g_tag_P, g_taa_P, g_tga_P = stop_Codon_Count(gene_Stops,gene_Lengths)
    o_atg_P, o_gtg_P, o_ttg_P, o_att_P, o_ctg_P = start_Codon_Count(orf_Starts,orf_Lengths)
    o_tag_P, o_taa_P, o_tga_P = stop_Codon_Count(orf_Stops,orf_Lengths)

    # output = ("Number of Protein Coding Genes in " + str(annotation) + " : " + str(len(gene_Lengths)) + ", Median Length of PCGs: " +
    #           str(gene_Median) + ", Min Length of PCGs: " + str('NA') + ", Max Length of PCGs: " + str('NA') +
    #           ", Number of PCGs on Pos Strand: " + str(strands['+']) + ", Number of PCGs on Neg Strand: " + str(strands['-']) +
    #           ", Median GC of PCGs: " + str('NA') +
    #           ", Number of PCGs less than 100nt: " + str('NA') +
    output = ("Number of Partial Hits:" + str(len(gene_Lengths)) + "\nMedian Length of Partial Hit Genes:" + str(gene_Median) +
              '\nMedian Length of Partial Hit ORFs:' +  str(orf_Median) + '\nMedian GC Partial Hit Genes:' + str(gene_Median_GC) +
              '\nMedian GC Partial Hit ORFs:' + str(orf_Median_GC) +
              '\nPercentage of Genes starting with ATG - Annotation/partial: ' + g_atg_P + ' ' + o_atg_P +
              '\nPercentage of Genes starting with GTG - Annotation/partial: ' + g_gtg_P + ' ' + o_gtg_P +
              '\nPercentage of Genes starting with TTG - Annotation/partial: ' + g_ttg_P + ' ' + o_ttg_P +
              '\nPercentage of Genes starting with ATT - Annotation/partial: ' + g_att_P + ' ' + o_att_P +
              '\nPercentage of Genes starting with CTG - Annotation/partial: ' + g_ctg_P + ' ' + o_ctg_P +
              #'\nPercentage of Genes starting with Alternative Start Codon - Annotation/partial: ' + other_Starts_P + ' ' + m_other_Stops_P +
              '\nPercentage of Genes ending with TAG - Annotation/partial: ' + g_tag_P + ' ' + o_tag_P +
              '\nPercentage of Genes ending with TAA - Annotation/partial: ' + g_taa_P + ' ' + o_taa_P +
              '\nPercentage of Genes ending with TGA - Annotation/partial: ' + g_tga_P + ' ' + o_tga_P )
              #'\nPercentage of Genes ending with Alternative Stop Codon - Annotation/partial: ' + other_Stops_P + ' ' + m_other_Stops_P)




    print(output)

    import matplotlib.pylab as plt

    list_ORF_Starts = list(orf_Starts.items())  # sorted by key, return a list of tuples
    list_Gene_Starts = list(gene_Starts.items())
    o_x, o_y = zip(*list_ORF_Starts)  # unpack a list of pairs into two tuples
    g_x, g_y = zip(*list_Gene_Starts)

    plt.plot(o_x, o_y)
    plt.plot(g_x, g_y)
    plt.show()

    list_ORF_Stops = list(orf_Stops.items())  # sorted by key, return a list of tuples
    list_Gene_Stops = list(gene_Stops.items())
    o_x, o_y = zip(*list_ORF_Stops)  # unpack a list of pairs into two tuples
    g_x, g_y = zip(*list_Gene_Stops)

    plt.plot(o_x, o_y)
    plt.plot(g_x, g_y)
    plt.show()


if __name__ == "__main__":
    result_compare(**vars(args))















