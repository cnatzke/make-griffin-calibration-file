import os
import pandas as pd
from math import floor
from pprint import pprint


def calibration_block(mnemonic, channel, address, digitizer, scalar, linear):
    return (
        f'{mnemonic} {{ \n'
        f'Name:\t{mnemonic}\n'
        f'Number:\t{channel}\n'
        f'Address:\t{address}\n'
        f'Digitizer:\t{digitizer}\n'
        f'EngCoeff:\t{scalar} {linear}\n'
        'Integration:\t0\n'
        'ENGChi2:\t0\n'
        'FileInt:\t0\n'
        '}\n\n'
        '//====================================//\n'
    )


def main():
    conf_file_name = "Conf_File.txt"
    parameter_dir = "/vagrant/analysis/two-photon-calibration/my-build/cal-parameters"
    cal_file_dir = "/vagrant/analysis/cal-files"

    # read in conf file for mnemonics and addresses
    conf_df = pd.read_csv(conf_file_name, engine='c', sep='|', header=None)
    conf_columns = ["channel", "address", "mnemonic", "linear", "scalar", "quadratic", "digitizer"]
    conf_df.columns = conf_columns
    print(f"Successfully read in configuration file: {conf_file_name}")

    file_list = os.listdir(parameter_dir)
    for my_file in file_list:
        run_number = my_file.split("_")[1].split(".")[0]
        parameter_df = pd.read_csv(f'{parameter_dir}/{my_file}', engine='c', sep="|")
        # open calibration file for writing
        cal_file_name = f'{cal_file_dir}/cal_file_{run_number}.cal'
        cal_file = open(cal_file_name, "w")

        for row_dict in conf_df.to_dict(orient="records"):
            temp_channel = row_dict['channel'] % 28  # crystal number [0,3] -- Use '% 14 for A+B channels'
            temp_position = floor(row_dict['channel'] / 14)  # detector position [0, 15]
            if temp_channel < 4 and row_dict['channel'] < (28 * 16):  # only get gains for Germanium channels
                cal_index = temp_channel + 2 * temp_position
                cal_file.write(calibration_block(row_dict['mnemonic'], row_dict['channel'], row_dict['address'],
                               row_dict['digitizer'], parameter_df.loc[cal_index, 'scalar'], parameter_df.loc[cal_index, 'linear']))
            else:
                cal_file.write(calibration_block(row_dict['mnemonic'], row_dict['channel'], row_dict['address'], row_dict['digitizer'], 0.0, 1.0))

        cal_file.close()

    print(f"Calibration files written to directory: {cal_file_dir}")


if __name__ == "__main__":
    main()
