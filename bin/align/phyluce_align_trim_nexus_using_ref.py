#!/usr/bin/env python
# encoding: utf-8
"""
File: phyluce_align_trim_nexus_using_ref.py
Author: Carl Oliveros

Description: Trims sequences from ends of target taxon/alignment based on the 
sequence of a reference taxon (that has missing data on its ends).

"""

import os
import sys
import glob
import argparse
from Bio.Nexus import Nexus
from Bio.Seq import Seq
from phyluce.helpers import is_dir, FullPaths, CreateDir
from phyluce.log import setup_logging

def get_args():
    parser = argparse.ArgumentParser(
        description='Trim sequences of target taxon/alignment based on reference taxon.')
    parser.add_argument(
        "--input", 
        required=True,
        type=is_dir, 
        action=FullPaths,
        help="The input directory containing nexus files")
    parser.add_argument(
        "--output", 
        required=True,
        action=CreateDir,
        help="The directory in which to store the output files")
    parser.add_argument(
        "--reference", 
        required=True,
        type=str,
        help="The reference taxon for trimming")
    parser.add_argument(
        "--target", 
        required=True,
        type=str,
        help="The target taxon for trimming. 'ALL' (case-sensitive) trims the entire alignment")
    parser.add_argument(
        '--trim-file',
        required=True,
        action=FullPaths,
        help="The file that will contain trimming information")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--exclude",
        type=str,
        default=[],
        nargs='+',
        help="Taxa to exclude")
    group.add_argument(
        "--include",
        type=str,
        default=[],
        nargs='+',
        help="Taxa to include")
    parser.add_argument(
        "--log-path",
        action=FullPaths,
        type=is_dir,
        default=None,
        help="The path to a directory to hold logs.")
    parser.add_argument(
        "--verbosity",
        type=str,
        choices=["INFO", "WARN", "CRITICAL"],
        default="INFO",
        help="The logging level to use.")
    return parser.parse_args()
    
def get_trim_size(ref_seq, side, missing):
    if side == 'left':
        trimmed = ref_seq.lstrip(missing)
    elif side == 'right':
        trimmed = ref_seq.rstrip(missing)
    trim_size = len(ref_seq) - len(trimmed)
    return trim_size
    
def get_trimmed_seq(fname, alignment, ref, target, outf):
    ref_seq = alignment.matrix[ref]._data
    trim_left = get_trim_size(ref_seq, 'left', alignment.missing)
    trim_right = get_trim_size(ref_seq, 'right', alignment.missing)
    target_seq = alignment.matrix[target]._data
    l = len(target_seq)
    if trim_left > 0:
        target_seq = alignment.missing * trim_left + target_seq[trim_left: l]
    if trim_right > 0:
        target_seq = target_seq[0: l - trim_right] + alignment.missing * trim_right
    trimmed_seq = Seq(target_seq, alignment.matrix[target].alphabet)
    outf.write('{}\t{}\t{}\n'.format(fname, trim_left, trim_right))
    return trimmed_seq
    
def get_samples_to_delete(args, all_names):
    if args.exclude:
        return set([name for name in all_names if name in args.exclude])
    elif args.include:
        return set([name for name in all_names if name not in args.include])
    else:
        return []

def get_all_taxon_names(data):
    taxa = set()
    for align_file in data:
        fname, align = align_file
        for taxon in align.taxlabels:
            taxa.add(taxon)
    return taxa
        
def main():
    args = get_args()
    log, my_name = setup_logging(args)
    log.info("Reading input alignments in NEXUS format")
    # read nexus files 
    nexus_files = glob.glob(os.path.join(os.path.expanduser(args.input), '*.nexus'))
    data = [(os.path.splitext(os.path.basename(fname))[0], Nexus.Nexus(fname)) for fname in nexus_files]
    log.info("{} alignments read".format(len(data)))
    taxa = get_all_taxon_names(data)
    delete_taxa = get_samples_to_delete(args, taxa)
    if args.target in delete_taxa:
        log.error('Target taxon {} is in delete list {}'.format(args.target, delete_taxa))
    outf = open(args.trim_file, 'w')
    outf.write('locus\ttrim_left\ttrim_right\n')
    log.info("Trimming in progress")
    for fname, alignment in data:
        # trim seq of target taxon/taxa
        if args.target == 'ALL':
            for taxon in alignment.taxlabels:
                alignment.matrix[taxon] = get_trimmed_seq(fname, alignment, args.reference, taxon, outf)
        else:
            alignment.matrix[args.target] = get_trimmed_seq(fname, alignment, args.reference, args.target, outf)
        # delete unwanted taxa
        alignment.matrix = alignment.crop_matrix(delete=delete_taxa)
        alignment.ntax = len(alignment.matrix)
        alignment.taxlabels = alignment.matrix.keys()
        # remove sites with gap/missing data for all taxa
        gaps = alignment.gaponly(include_missing=True)
        if len(gaps) > 0:
            alignment.matrix = alignment.crop_matrix(exclude=gaps)
            alignment.nchar = len(alignment.matrix[alignment.taxlabels[0]]._data)
        # write out nexus
        alignment.write_nexus_data(os.path.join(args.output, fname + '.nexus'))
        # write progress dots to stdout
        sys.stdout.write(".")
        sys.stdout.flush()
    print('')
    text = " Completed {} ".format(my_name)
    log.info(text.center(65, "="))
        
if __name__ == '__main__':
    main()
