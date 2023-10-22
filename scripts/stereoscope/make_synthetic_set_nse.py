#!/usr/bin/env python3

import os
import sys
import os.path as osp

import pandas as pd
import numpy as np
import torch as t


# Split SC data into a "validation" and "generation" set
# the generation set can be used to generate fake ST data
# whilst the validation set can be used for evaluation of the method



def main(sc_cnt_pth : str,
         sc_lbl_pth : str,
         out_dir : str,
        )-> None:

    """Generate single cell data for comparison

    Takes one single cell data set as input
    and generates a generation and validation
    set with non-overlapping members


    Parameter:
    --------
    sc_cnt_pth : str
        path to single cell count data
    sc_lbl_pth : str
        path to single cell label data
    out_dir : str
        path to output directory

    """

    # read data
    sc_cnt = pd.read_csv(sc_cnt_pth,
                         sep = ',',
                         index_col = 0,
                         header = 0)

    sc_lbl = pd.read_csv(sc_lbl_pth,
                         sep = ';',
                         index_col = 0,
                         header = 0)
                         
                             
    adata_df = pd.DataFrame(sc_cnt.T)

    sc_lbl2 = sc_lbl.loc[sc_lbl.iloc[:, 9] != 'Unclassified']

    # match count and label data
    inter = adata_df.index.intersection(sc_lbl2.index)

    sc_lbl = sc_lbl2.loc[inter,:]
    sc_cnt = adata_df.loc[inter,:]

 
    #labels = sc_lbl
    labels = sc_lbl.iloc[:,9]

    # get unique labels
    uni_labs, uni_counts = np.unique(labels,
                                     return_counts = True)

    # only keep types with more than 30 cells
    keep_types = uni_counts > 30
    keep_cells = np.isin(labels, uni_labs[keep_types])

    labels = labels[keep_cells]
    sc_cnt = sc_cnt.iloc[keep_cells,:]
    sc_lbl = sc_lbl.iloc[keep_cells,:]

    uni_labs, uni_counts = np.unique(labels,
                                     return_counts = True)

    n_types = uni_labs.shape[0]

    assert np.all(uni_counts > 2), \
            "Only one cell in types"


    # get member indices for each set
    idx_generation = []
    idx_validation = []

    np.random.seed(1337)

    for z in range(n_types):
        tmp_idx = np.where(labels == uni_labs[z])[0]
        n_generation = int(round(tmp_idx.shape[0]))
        idx_generation += tmp_idx[0:n_generation].tolist()
        idx_validation += tmp_idx[n_generation::].tolist()

    idx_generation.sort()
    idx_validation.sort()

    # make sure no members overlap between sets
    assert len(set(idx_generation).intersection(set(idx_validation))) == 0, \
            "validation and genreation set are not orthogonal"

    # assemble sets from indices
    cnt_validation = sc_cnt.iloc[idx_validation,:]
    cnt_generation = sc_cnt.iloc[idx_generation,:]

    lbl_validation = sc_lbl.iloc[idx_validation,:]
    lbl_generation = sc_lbl.iloc[idx_generation,:]

    # save sets
    cnt_validation.to_csv(osp.join(out_dir,
                                   '.'.join(['validation',
                                             osp.basename(sc_cnt_pth)]
                                           )
                                  ),
                          sep = ',',
                          header = True,
                          index = True,
                          index_label = 'cell')

    cnt_generation.to_csv(osp.join(out_dir,
                                   '.'.join(['generation',
                                             osp.basename(sc_cnt_pth)]
                                           )
                                  ),
                          sep = ',',
                          header = True,
                          index = True,
                          index_label = 'cell')

    lbl_validation.to_csv(osp.join(out_dir,'.'.join(['validation',
                                                     osp.basename(sc_lbl_pth)]
                                                   )
                                  ),

                          sep = ',',
                          header = True,
                          index = True,
                          index_label = 'cell')

    lbl_generation.to_csv(osp.join(out_dir,'.'.join(['generation',
                                                     osp.basename(sc_lbl_pth)]
                                                   )
                                  ),
                          sep = ',',
                          header = True,
                          index = True,
                          index_label = 'cell')

if __name__ == '__main__':
    main(sc_cnt_pth = sys.argv[1],
         sc_lbl_pth = sys.argv[2],
         out_dir = sys.argv[3],
        )

