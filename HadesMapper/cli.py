"""Command-line interface for Mapper functionality"""
import os
import argparse

from .HadesMapper import DecodeBinaries, EncodeBinaries

def main():
  parser = argparse.ArgumentParser(prog='HadesMapper', description="Unpack Hades's map binaries into JSON and pack JSON into game usable map binaries")
  subparsers = parser.add_subparsers(help='The action to perform', dest='action')

  # encode parser
  encode_parser = subparsers.add_parser('encode', help='Encode JSON into a binary file', aliases=['ec'])
  encode_parser.add_argument('-i', '-input', metavar='input', default='input.thing_text', type=str, help='The JSON file to encode, default is input.thing_text')
  encode_parser.add_argument('-o', '-output', metavar='output', default='output.thing_bin', type=str, help='The binary file to output, default is output.thing_bin')
  encode_parser.add_argument('-s', '-sequel', action='store_true', help='Flag for whether the game is the sequel (Hades II), default is Hades 1')
  encode_parser.set_defaults(func=cli_encode)

  #decode parser
  decode_parser = subparsers.add_parser('decode', help='Encode JSON into a binary file', aliases=['dc'])
  decode_parser.add_argument('-i', '-input', metavar='input', default='input.thing_bin', type=str, help='The binary file to decode, default is input.thing_bin')
  decode_parser.add_argument('-o', '-output', metavar='output', default='output.thing_text', type=str, help='The JSON file to output to, default is output.thing_text')
  decode_parser.add_argument('-s', '-sequel', action='store_true', help='Flag for whether the game is the sequel (Hades II), default is Hades 1')
  decode_parser.set_defaults(func=cli_decode)

  args = parser.parse_args()

  args.func(args)

def cli_encode(args):
  input = args.i
  output = args.o
  sequel = args.s

  EncodeBinaries(input, output, sequel)

def cli_decode(args):
  input = args.i
  output = args.o
  sequel = args.s

  DecodeBinaries(input, output, sequel)