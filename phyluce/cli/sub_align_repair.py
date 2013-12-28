#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
(c) 2013 Brant Faircloth || http://faircloth-lab.org/
All rights reserved.

This code is distributed under a 3-clause BSD license. Please see
LICENSE.txt for more information.

Created on 28 December 2013 13:12 PST (-0800)
"""


from __future__ import absolute_import

from phyluce.align import repair
from phyluce.common import is_dir, is_file, FullPaths, CreateDir


descr = "Repair problematic alignments (convert to N-bases)."


def configure_parser(sub_parsers):
    sp = sub_parsers.add_parser(
        "repair",
        description=descr,
        help=descr,
    )

    sp.add_argument(
        '--alignments',
        required=True,
        type=is_dir,
        action=FullPaths,
        help="The directory containing alignments to be screened."
    )
    sp.add_argument(
        '--config',
        required=True,
        type=is_file,
        action=FullPaths,
        help="The config file output from `phyluce align check`."
    )
    sp.add_argument(
        '--output',
        required=True,
        action=CreateDir,
        help="The directory in which to store the resulting alignments."
    )
    sp.add_argument(
        "--input-format",
        dest="input_format",
        choices=['fasta', 'nexus', 'phylip', 'clustal', 'emboss', 'stockholm'],
        default='nexus',
        help="The input alignment format",
    )
    sp.add_argument(
        "--cores",
        type=int,
        default=1,
        help="Process alignments in parallel using --cores for alignment. "
             "This is the number of PHYSICAL CPUs."
    )
    sp.add_argument(
        '--section',
        type=str,
        default="Problematic loci",
        help="The config file section."
    )
    sp.add_argument(
        "--log-path",
        action=FullPaths,
        type=is_dir,
        default=None,
        help="The path to a directory to hold logs."
    )
    sp.add_argument(
        "--verbosity",
        type=str,
        choices=["INFO", "WARN", "CRITICAL"],
        default="INFO",
        help="The logging level to use."
    )

    sp.set_defaults(func=repair_alignments)


def repair_alignments(args, parser):
    repair.main(args, parser)
