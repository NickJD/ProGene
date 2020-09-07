import collections
import csv
import argparse
from importlib import import_module
from Comparator import tool_comparison

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--tool', required=True, help='Which tool to compare?')
parser.add_argument('-i', '--input_to_analyse', required=True, help='File name of tool predictions to compare.')
parser.add_argument('-g', '--genome_to_compare', required=True, help='Which genome to analyse? Genome files have same prefix'
                                                                     ' - .fa and .gff appended')
args = parser.parse_args()

def comparator(tool,input_to_analyse,genome_to_compare):
    genome_Seq = ""
    with open('genomes/'+genome_to_compare+'.fa', 'r') as genome: # Only works for single contig genomes
        for line in genome:
            line = line.replace("\n","")
            if not line.startswith('>'):
                genome_Seq += str(line)
    ##############################################
    genes = collections.OrderedDict() # Order is important
    count = 0
    with open('genomes/'+genome_to_compare+'.gff','r') as genome_gff: # Should work for GFF3
        for line in genome_gff:
            line = line.split('\t')
            try:
                if "CDS" in line[2] and len(line) == 9:
                    start = int(line[3])
                    stop = int(line[4])
                    strand = line[6]
                    gene = str(start) + ',' + str(stop) + ',' + strand
                    genes.update({count: gene})
                    count +=1
            except IndexError:
                continue
    #############################################
    tool_predictions = import_module('Tools.'+tool+'.'+tool)
    tool_predictions = getattr(tool_predictions,tool)
    orfs = tool_predictions(input_to_analyse,genome_Seq)
    all_Metrics, all_rep_Metrics, start_precision, stop_precision,other_starts, other_stops, missed_genes, unmatched_orfs, undetected_gene_metrics, unmatched_orf_metrics, gene_coverage_genome, multi_Matched_ORFs = tool_comparison(genes,orfs,genome_Seq)
    outname = input_to_analyse.split('.')[0]
    metric_description = list(all_Metrics.keys())
    metrics = list(all_Metrics.values())
    rep_metric_description = list(all_rep_Metrics.keys())
    rep_metrics = list(all_rep_Metrics.values())
    with open("Tools/"+tool+'/'+outname+'.csv', 'w', newline='\n', encoding='utf-8') as out_file: # Clear write out of report
        tool_out = csv.writer(out_file, quoting=csv.QUOTE_NONE, escapechar=" ")
        #tool_out.writerow(['Abbreviations:']) Future Work
        #tool_out.writerow(['PD:Percentage Difference,MO:Matched ORFs,'])
        tool_out.writerow(['Representative Metrics:'])
        tool_out.writerow(rep_metric_description)
        tool_out.writerow(rep_metrics)
        tool_out.writerow(['All Metrics:'])
        tool_out.writerow(metric_description)
        tool_out.writerow(metrics)
        tool_out.writerow(['CDS Gene Coverage of Genome: '])
        tool_out.writerow([gene_coverage_genome])
        tool_out.writerow(['Start Position Difference:'])
        tool_out.writerow(start_precision)
        tool_out.writerow(['Stop Position Difference:'])
        tool_out.writerow(stop_precision)
        tool_out.writerow(['Alternative Starts Predicted:'])
        tool_out.writerow(other_starts)
        tool_out.writerow(['Alternative Stops Predicted:'])
        tool_out.writerow(other_stops)
        tool_out.writerow(['Undetected Gene Metrics:'])
        tool_out.writerow(['ATG Start,GTG Start,TTG Start,ATT Start,CTG Start,Alternative Start Codon,TGA Stop,TAA Stop,TAG Stop,Alternative Stop Codon,Median Length,Genes on Positive Strand,Genes on Negative Strand'])
        tool_out.writerow(undetected_gene_metrics)
        tool_out.writerow(['Undetected Genes:'])
        for key,value in missed_genes.items():
            key = key.split(',')
            id = ('>' + genome_to_compare + '_' + key[0] + '_' + key[1] + '_' + key[2])
            tool_out.writerow([id + '\n' + value])
        tool_out.writerow(['\n\n\nORFs without corresponding gene in Ensembl Metrics:'])
        tool_out.writerow(['ATG Start,GTG Start,TTG Start,ATT Start,CTG Start,Alternative Start Codon,TGA Stop,TAA Stop,TAG Stop,Alternative Stop Codon,Median Length,ORFs on Positive Strand,ORFs on Negative Strand'])
        tool_out.writerow(unmatched_orf_metrics)
        tool_out.writerow(['ORFs without corresponding gene in Ensembl:'])
        for key, value in unmatched_orfs.items():
            key = key.split(',')
            id = ('>'+tool+'_'+key[0]+'_'+key[1]+'_'+key[2])
            tool_out.writerow([id + '\n' + value])
        tool_out.writerow(['\nORFs Which Detected more than one Gene:'])

        try:
            for key, value in multi_Matched_ORFs.items():
                key = key.split(',') # Temp fix
                value = value[1].split(',')
                multi = ('ORF:'+key[0]+'-'+key[1]+'_Gene:'+value[0]+'-'+value[1])
                tool_out.writerow([multi])
        except IndexError:
            pass



if __name__ == "__main__":
    comparator(**vars(args))
