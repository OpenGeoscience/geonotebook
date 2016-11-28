import numpy as np

point = { 'rect': [22.0, 22.0],
          'coords': [22.0, 22.0, 22.0, 22.0, 22.0],
          'single': 22.0,
          'missing': [22.0, 22.0, 22.0, 22.0]}

rect = { 'rect': [[[  1.,  2.],
                   [ 21., 21.]],
                  [[ 12., 12.],
                   [ 22., 22.]]],
         'coords': [[[  1.,  2.,  3.,  4.,  5.],
                     [ 21., 21., 21., 21., 21.]],
                    [[ 12., 12., 12., 12., 12.],
                     [ 22., 22., 22., 22., 22.]]],
         'single': [[  1., 21.],
                    [ 12., 22.]],
         'missing': [[[  1.,  2.,  3.,  4.],
                      [ 21., 21., 21., 21.]],
                     [[ 12., 12., 12., 12.],
                      [ 22., 22., 22., 22.]]] }

polygon = {
    'rect': np.ma.masked_array(
        data=[[[1.0, 2.0], [-9999., -9999.], [-9999.,  -9999.]],
              [[12., 12.], [   22.,    22.], [-9999.,  -9999.]],
              [[13., 13.], [   23.,    23.], [   33.,     33.]]],
        mask=[[[False, False], [ True,  True], [ True, True]],
              [[False, False], [False, False], [ True, True]],
              [[False, False], [False, False], [False, False]]],
        fill_value = -9999.0),

    'coords': np.ma.masked_array(
        data = [[[ 1.0,  2.0,  3.0,  4.0,  5.0], [-9999., -9999., -9999., -9999., -9999.], [-9999., -9999., -9999., -9999., -9999.]],
                [[12.0, 12.0, 12.0, 12.0, 12.0], [   22.,    22.,    22.,    22.,    22.], [-9999., -9999., -9999., -9999., -9999.]],
                [[13.0, 13.0, 13.0, 13.0, 13.0], [   23.,    23.,    23.,    23.,    23.], [   33.,    33.,    33.,    33.,    33.]]],
        mask = [[[False, False, False, False, False], [ True,  True,  True,  True,  True], [ True,  True,  True,  True,  True]],
                [[False, False, False, False, False], [False, False, False, False, False], [ True,  True,  True,  True,  True]],
                [[False, False, False, False, False], [False, False, False, False, False], [False, False, False, False, False]]],
        fill_value = -9999.0),

    'single': np.ma.masked_array(
        data = [[ 1., -9999., -9999.],
                [12.,    22., -9999.],
                [13.,    23.,    33.]],
        mask =[[False,  True,  True],
               [False, False,  True],
               [False, False, False]],
        fill_value = -9999.0),

    'missing': np.ma.masked_array(
        data = [[[ 1.,  2.,  3.,  4.], [-9999., -9999., -9999., -9999.], [-9999., -9999., -9999., -9999.]],
                [[12., 12., 12., 12.], [   22.,    22.,    22.,    22.], [-9999., -9999., -9999., -9999.]],
                [[13., 13., 13., 13.], [   23.,    23.,    23.,    23.], [   33.,    33.,    33.,    33.]]],
        mask = [[[False, False, False, False], [ True,  True,  True,  True], [ True,  True,  True,  True]],
                [[False, False, False, False], [False, False, False, False], [ True,  True,  True,  True]],
                [[False, False, False, False], [False, False, False, False], [False, False, False, False]]],
        fill_value = -9999.0)
    }
