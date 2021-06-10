"""
Ot2Rec.metadata.py

Copyright (C) Rosalind Franklin Institute 2021

Author: Neville B.-y. Yee
Date: 10-Jun-2021

Version: 0.0.1
"""


import yaml
import os
from glob import glob
import pandas

import Ot2Rec.params as prmMod


class Metadata:
    """
    Class encapsulating Metadata objects
    """

    # First define conversion table between job (module) name and file suffixes
    suffix_dict = {
        'master': 'proj',
        'motioncorr': 'mc',
        'ctffind': 'ctffind',
        'align': 'align',
        'reconstruct': 'recon',
    }
        

    def __init__(self,
                 project_name: str,
                 job_type: str,
    ):
        """
        Initialise Metadata object

        ARGS:
        project_name :: name of the current project
        job_type     :: what job is being done (motioncorr/ctffind/align/reconstruct)
        """

        self.project_name = project_name
        self.job_type = job_type

        # Obtain parameters first
        self.get_param()
        self.params = self.prmObj.params


    def get_param(self):
        """
        Subroutine to get parameters for current job
        """

        param_file = self.project_name + '_' + suffix_dict[self.job_type] + '.yaml'
        self.prmObj = prmMod.read_yaml(param_file)
        

    def create_master_metadata(self):
        """
        Function to create master metadata from raw data.
        Metadata include: image paths, tilt series indices, tilt angles

        OUTPUTS:
        pandas DataFrame
        """

        # Define criteria for searching subfolders (tilt series) within source folder
        if self.params['TS_folder_prefix'] == '*':
            ts_subfolder_criterion = '*'
        elif self.params['TS_folder_prefix'] != '*' and \
             len(self.params['TS_folder_prefix']) > 0:
            ts_subfolder_criterion = self.params['TS_folder_prefix'] + '_*'
            
        if self.params['source_TIFF']:
            source_extension = 'tif'
        else:
            source_extension = 'mrc'

        # Find files and check
        raw_images_list = glob("{}{}.{}".format(self.params['source_folder'],
                                                ts_subfolder_criterion,
                                                source_extension)
        )
        assert (len(raw_images_list) > 0), \
            raise IOError("Error in Ot2Rec.metadata.Metadata.create_master_metadata: No vaild files found using given criteria.")


        # Extract information from image file names
        self.image_paths, self.tilt_series, self.tilt_angles = [], [], []
        for curr_image in raw_images_list:
            self.image_paths.append(curr_image)

            # Extract tilt series number
            split_path_name = curr_image.split('/')[-1].split('_')
            try:
                ts_index = int(''.join(i for i in split_path_name[self.params['image_stack_field']] if i.isdigit()))
            except IndexError or ValueError as ierr:
                raise IndexError(f"Error in Ot2Rec.metadata.Metadata.create_master_metadata: Error code: {ierr}. Failed to get tilt series number from file path {curr_image}.")
            self.tilt_series.append(ts_index)

            # Extract tilt angle
            try:
                tilt_angle = float(split_path_name[self.params['Inputs']['image_tiltangle_field']].replace(
                    f'.{extension}', '').replace('[', '').replace(']', ''))
            except IndexError or ValueError as ierr:
                raise IndexError(f"Error in Ot2Rec.metadata.Metadata.create_master_metadata: Error code: {ierr}. Failed to get tilt angle from file path {curr_image}.")
            self.tilt_angles.append(tilt_angle)
        
        return pd.DataFrame(dict(file_paths=self.image_paths,
                                 ts=self.tilt_series,
                                 angles=self.tilt_angles))

        
