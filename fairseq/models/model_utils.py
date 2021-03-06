# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import torch


def skip_tensors(x, mask):
    """
    Getting sliced (dim=0) tensor by mask. Supporting tensor and list/dict of tensors.
    """
    if isinstance(x, int):
        return x

    if x is None:
        return None

    if isinstance(x, torch.Tensor):
        if x.size(0) == mask.size(0):
            return x[mask]
        elif x.size(1) == mask.size(0):
            return x[:, mask]

    if isinstance(x, list):
        return [skip_tensors(x_i, mask) for x_i in x]

    if isinstance(x, dict):
        return {k: skip_tensors(v, mask) for k, v in x.items()}

    raise NotImplementedError


def expand_2d_or_3d_tensor(x, trg_dim, padding_idx):
    """
    Expand 2D/3D tensor on dim=1
    """
    if x is None:
        return None

    assert x.dim() == 2 or x.dim() == 3
    assert trg_dim >= x.size(1), (trg_dim, x.size())
    if trg_dim == x.size(1):
        return x

    dims = [x.size(0), trg_dim - x.size(1)]
    if x.dim() == 3:
        dims.append(x.size(2))
    x = torch.cat([x, x.new_zeros(*dims).fill_(padding_idx)], 1)

    return x


def fill_tensors(x, mask, y, padding_idx):
    """
    Filling tensor x with y at masked positions (dim=0).
    """
    if x is None:
        return None

    assert x.dim() == y.dim() and mask.size(0) == x.size(0)
    assert x.dim() == 2 or (x.dim() == 3 and x.size(2) == y.size(2))

    n_selected = mask.sum()
    if n_selected == 0:
        return x
    assert n_selected == y.size(0)
    if n_selected == x.size(0):
        return y

    if x.size(1) < y.size(1):
        x = expand_2d_or_3d_tensor(x, y.size(1), padding_idx)
        x[mask] = y
    elif x.size(1) > y.size(1):
        x[mask] = padding_idx
        if x.dim() == 2:
            x[mask, :y.size(1)] = y
        else:
            x[mask, :y.size(1), :] = y
    else:
        x[mask] = y
    return x
