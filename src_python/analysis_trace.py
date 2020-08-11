#import matplotlib
import json

import utils

def main():
    result_file_path =  "result/udp_client_recieve.txt"
    output_trace_path = "output_trace/udp_trace.txt"
    result_analysis(result_file_path, output_trace_path)

def result_analysis(result_file_path, output_trace_path):
    # analysis result file and generate trace:
    current_line = 0
    current_connection = 0
    Bandwidth_list = []
    with open(result_file_path, "r") as input, open(output_trace_path, "w") as output:
        for line in input:
            if current_line == 0:
                try:
                    trace_config = json.loads(line[:-1])
                    print(trace_config["client_start_time"])
                except:
                    print("Error: Cannot phase Config!!!")
                    exit()
            else:
                try:
                    attribute, value = line.split('\t')[:-1]
                    if attribute == "BW":
                        Bandwidth_list.append(float(value))
                    if attribute == "Connection":
                        current_connection = value
                except:
                    print("Line format is not right, ignore this line")
            current_line = current_line + 1
    
















if __name__ == '__main__':
