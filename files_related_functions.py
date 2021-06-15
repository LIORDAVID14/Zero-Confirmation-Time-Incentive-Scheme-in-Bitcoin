import tarfile
import glob
import os
import configparser
import sys
import fnmatch
import errno
from decimal import *


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def round_down(num, divisor):
    return int(num) - (int(num) % int(divisor))


def block_count_and_time_stamp_from_file_name(file_name):
    basename = os.path.basename(file_name)
    result = basename.split("_")
    index_list = range(6)
    time_stamps_list = [result[index + 2] for index in index_list]
    time_stamps_list[-1] = time_stamps_list[-1].split(".")[0]
    joined_time_stamp = '-'.join(time_stamps_list)
    block_count = result[0]
    assert (result[0] == result[1])
    return block_count, joined_time_stamp


def find_files(data_dir_path, filter_function):
    matches = []
    for root, _, file_names in os.walk(data_dir_path):
        for file_name in [x for x in file_names if filter_function(x)]:
            matches.append(os.path.join(root, file_name))
    matches.sort()
    return matches


def get_params(sys):
    assert (len(sys.argv) == 3)
    first_block = sys.argv[1]
    last_block = sys.argv[2]

    return first_block, last_block


def block_in_range_and_suffix(x, first_block, last_block, suffix):
    # print "first_block",first_block,x.split("_")[0]
    first_block_int = int(first_block)
    last_block_int = int(last_block)
    split_x = x.split("_")
    x_pre_int = int(split_x[0])
    x_post_int = int(split_x[1])

    return x_pre_int >= first_block_int and \
           x_pre_int <= last_block_int and \
           x.endswith(suffix) and \
           x_pre_int == x_post_int


def get_output_file_path(output_dir_path=None, time_stamp=None, block_count=0, suffix=None):
    if time_stamp is not None:
        file_name = str(time_stamp) + "_" + str(block_count) + suffix
    else:
        file_name = str(block_count) + suffix
    rounded_block_number = round_down(block_count, 100)
    file_path = os.path.join(output_dir_path, str(rounded_block_number), file_name)
    return file_path


# https://stackoverflow.com/questions/803616/passing-functions-with-arguments-to-another-function-in-python


def create_file(output_file_path, function_to_create_file):
    mkdir_p(os.path.dirname(output_file_path))
    if os.path.isfile(output_file_path):
        print (output_file_path, "already exists")
    else:
        function_to_create_file()
        print (output_file_path, "created")


def filter_by_block_number_and_suffix(first_block, last_block, suffix):
    return lambda x: block_in_range_and_suffix(x, first_block, last_block, suffix)


def read_dict_from_file(file_path):
    untarred_file_path = file_path.replace(".tar.gz", "")
    txs_dict = None
    with open(untarred_file_path, 'r') as myfile:
        data = myfile.read()
        txs_dict = eval(data)
    assert (txs_dict is not None)
    return txs_dict


def create_untarred_file(file_path):
    dir_path = os.path.dirname(os.path.realpath(file_path))
    tar = tarfile.open(file_path)
    tar.extractall(path=dir_path)
    tar.close()


def delete_untarred_file(file_path):
    untarred_file_path = file_path.replace(".tar.gz", "")
    assert (os.path.exists(untarred_file_path))
    os.remove(untarred_file_path)


# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')


# Restore
def enablePrint():
    sys.stdout = sys.__stdout__
