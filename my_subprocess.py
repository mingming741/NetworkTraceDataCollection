#! /usr/bin/python3
# act as some subprocess handler to do internal job when running large job

import os
import argparse

def main():
    parser = argparse.ArgumentParser(description='For different background job')
    parser.add_argument('mission', type=str, help='the job')
    parser.add_argument('--file-path', type=str, help='for some file path')
    parser.add_argument('--mode', type=str, help='mode for mission')
    parser.add_argument('--post', type=int, help='whether post to server')
    parser.add_argument('--network', type=int, help='network')
    parser.add_argument('--direction', type=int, help='direction')
    parser.add_argument('--variant', type=int, help='variant')

    # translate pcap file to txt, using non-blocking multi processing
    args = parser.parse_args()
    if args.mission == "pcap2txt":
        if args.mode == 'tcp':
            if os.path.exists(args.file_path):
                txt_dir = args.file_path[0:-4] + 'txt'
                os.system("tshark -r " + args.file_path + " -T fields -e frame.time_epoch -e frame.cap_len > " + txt_dir)
                os.system("rm " + args.file_path)
                if args.post == 1:
                    myweb.post_file_to_server(txt_dir, args.network, args.direction, args.variant)

        if args.mode == 'udp':
            if os.path.exists(args.file_path):
                txt_dir = args.file_path[0:-4] + 'txt'
                #os.system("tshark -r " + args.file_path + " -T fields -e frame.time_relative -e frame.cap_len > " + txt_dir)
                os.system("tshark -r " + args.file_path + " -T fields -e frame.time_epoch -e frame.cap_len > " + txt_dir)
                os.system("rm " + args.file_path)
                if args.post == 1:
                    myweb.post_file_to_server(txt_dir, args.network, args.direction, args.variant)

    # generate a large file for wget testing
    if args.mission == "generate_large_file":
        if os.path.exists('f_max'):
            os.system("rm f_max")
        with open('f_max', 'w') as f:
            for i in range (0, 4 * 1024 * 1024):
                b_num = str(i % 10)
                f.write(b_num * 1024)

if __name__ == '__main__':
    main()
