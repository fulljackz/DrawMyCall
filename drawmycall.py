#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Created by Unam on Wed Jan 19 2022
# Copyright (c) 2022 Unam - https://github.lacavernedemanu.fr
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software
# and associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial
# portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import pyshark, sys, datetime, os, fileinput, subprocess, argparse

def main(capture, time = "False"):
    # Set vars 
    mermaidConfig = os.getcwd() + "/mermaid-config.json"
    outName = os.path.basename(capture)
    out = open(outName,'w')
    sequences = []
    timestamp = []
    i = 0
    
    # Key / value for pload (rtp)
    pload = {
        "0": "ITU-T G.711 PCMU",
        "5": "DVI4 8000 samples/s",
        "6": "DVI4 16000 samples/s",
        "8": "ITU-T G.711 PCMA",
        "9": "ITU-T G.722",
        "99": "G726-16",
        "99": "iLBC",
        "99": "L16",
        "99": "opus",
        "99": "speex",
        "126": "DynamicRTP-Type-126"
    }

    # Then run main
    pcapFile = pyshark.FileCapture(capture)
    # Parse .pcap 
    for num in pcapFile:
        # check if packet has rtp attribute
        if hasattr(num, 'rtp') and int(num.length) >= 100:
            diff = "-->"
            diagSeq = [num['IP'].src, num['IP'].dst, pload[num['RTP'].p_type], diff, num['RTP'].ssrc, num['UDP'].stream, num['RTP'].p_type ]
        
        # check if packet has sip attribute
        if hasattr(num, 'sip'):
            diff = "->>"
            if hasattr(num['sip'], 'status_line'):
                status = num['sip'].status_line
            else:
                status = num['sip'].method
            diagSeq = [num['IP'].src, num['IP'].dst, status, diff, "", "", num['SIP'].via ]

        # Append to sequences only if diagSeq(sip or rtp) is not in sequences (avoid duplicates flaws)
        if diagSeq not in sequences:
            sequences.append(diagSeq)
            timestamp.append(num.frame_info.time_relative)
    
    # Get first ip of .pcap then write sequences list to file with mermaid synthax
    y = sequences[0][0]
    out.write("{}".format("sequenceDiagram\n"))
    for x in sequences:
        out.write("{} {} {} {} {} {}".format(x[0], x[3], x[1], ":", x[2], "\n"))
        if time:
            out.write("{} {} {} {} {}".format("Note left of ", y, ":", timestamp[i], "\n"))
        i+=1
    out.close()
    subprocess.run([os.path.expanduser( '~' ) + "/node_modules/.bin/mmdc", "-o", "./output/" + outName + ".png", "-i", outName, "-c", mermaidConfig])
    os.remove(outName) 

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Show args as required : https://bugs.python.org/issue9694
    req_grp = parser.add_argument_group(title='required arguments')
    req_grp.add_argument("-f", "--file", required=True, help="path to your pcap file")
    parser.add_argument("-t", "--time", help="Add time on diagram",
            action="store_true")
    args = parser.parse_args()
    main(args.file, args.time)
