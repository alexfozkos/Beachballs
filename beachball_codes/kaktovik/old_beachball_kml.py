#syntax: /Users/glea/anaconda2/bin/python old_beachball_kml.py /Users/glea/.../?.csv /Users/glea/.../outputfolder
#usage: old_beachball_kml.py [-h] [-s -S] [-c -C] input_path output_path    -h help, -s scale factor, -c color
from obspy.imaging.beachball import beachball
import argparse
import sys
import csv
import matplotlib
from lxml import etree
from pykml.factory import KML_ElementMaker as KML
from collections import defaultdict
import itertools
import os

def main():
    args = get_arguments()
    with open(args.input_path, "r") as csv_file:
        csv_dict = csv.DictReader(csv_file)
        csv_dict1, csv_dict2 = itertools.tee(csv_dict, 2) #copying iterator to keep beachball and kml generation separate (slower but easier to read)
        make_beachballs(csv_dict1, args) #no return value, saves beachballs to output directory path
        create_kml(csv_dict2, args) #no return value, saves .kml to output directory path

#see pykml documentation for reference
def create_kml(csv_dict, args):
    km = KML.kml(
        KML.Document(
        )
    )
    fld = KML.Folder()
    for row in csv_dict:
        icon_path = "beachballs/%s.png" % (row["orid.evid"])
        km.Document.append(
            KML.Placemark(
                KML.Name(row["orid.evid"]),
                KML.Point(
                    KML.coordinates("%s, %s" % (row["orid.lon"], row["orid.lat"]))
                ),
                KML.Style(
                    KML.IconStyle(
                        KML.Icon(
                            KML.href(icon_path),
                            KML.scale(args.s)
                        ),
                        KML.heading(0.0)
                    )
                )
            )
        )
    with open("%s/doc.kml" % args.output_path, "w") as kml_file:
        kml_file.write(etree.tostring(km, pretty_print=True))

#makes a beachball sub-directory at output path if none exists, then writes new beachballs to it (overwrites existing)
def make_beachballs(csv_dict, args):
    if not os.path.exists("%s/beachballs" % args.output_path):
        os.makedirs("%s/beachballs" % args.output_path)
    for row in csv_dict:
        mt = [float(row["fplane.str1"]), float(row["fplane.dip1"]), float(row["fplane.rake1"])]
        beachball(mt, facecolor=args.c, outfile="%s/beachballs/%s.png" % (args.output_path,row["orid.evid"]))
        matplotlib.pyplot.close("all") #necessary to go with nuclear option since I'm spawning a zombie with the preceeding call

#see argparse documentation for reference
def get_arguments():
    parser = argparse.ArgumentParser(description='creates beachball .pngs and .kml from an Antelope .csv file')
    parser.add_argument('input_path', type=str, help='relative or full .csv path')
    parser.add_argument('output_path', type=str, help='relative or full output folder path')
    parser.add_argument('-s', type=float, default=1.0, help='scale factor of beachballs on map as a decimal value where 1 is al size (default 1)')
    parser.add_argument('-c', type=str, default='k', help='face color of beachball(default black)')
    return parser.parse_args()

if __name__ == "__main__":
    status = main()
    sys.exit(status)

