import torch
import torch.optim as optim
import torch.nn as nn
import pandas as pd
from core.MSDN import MSDN
from core.CUBDataLoader import CUBDataLoader
from core.helper_MSDN_CUB import eval_zs_gzsl,visualize_attention#,get_attribute_attention_stats
# from global_setting import NFS_path
import importlib
import pdb
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import skimage
from sklearn.manifold import TSNE
from torchvision import transforms
import torch.nn.functional as F



NFS_path = './'

idx_GPU = 0
device = torch.device("cuda:{}".format(idx_GPU) if torch.cuda.is_available() else "cpu")
dataloader = CUBDataLoader(NFS_path,device,is_unsupervised_attr=False,is_balance=False)
dataloader.augment_img_path()
torch.backends.cudnn.benchmark = True

def get_lr(optimizer):
    lr = []
    for param_group in optimizer.param_groups:
        lr.append(param_group['lr'])
    return lr

seed = 214#215#
torch.manual_seed(seed)
torch.cuda.manual_seed_all(seed)
np.random.seed(seed)

batch_size = 50
nepoches = 70#22
niters = dataloader.ntrain * nepoches//batch_size
dim_f = 2048
dim_v = 300
init_w2v_att = dataloader.w2v_att
att = dataloader.att
normalize_att = dataloader.normalize_att

trainable_w2v = True
lambda_ = 0.1#0.1
bias = 0
prob_prune = 0
uniform_att_1 = False
uniform_att_2 = False

seenclass = dataloader.seenclasses
unseenclass = dataloader.unseenclasses
desired_mass = 1
report_interval = niters//nepoches


model_gzsl = MSDN(dim_f,dim_v,init_w2v_att,att,normalize_att,
            seenclass,unseenclass,
            lambda_,
            trainable_w2v,normalize_V=False,normalize_F=True,is_conservative=True,
            uniform_att_1=uniform_att_1,uniform_att_2=uniform_att_2,
            prob_prune=prob_prune,desired_mass=desired_mass, is_conv=False,
            is_bias=True)
model_gzsl.to(device)
model_gzsl.load_state_dict(torch.load('saved_model/CUB_MSDN_GZSL.pth'))

model_czsl = MSDN(dim_f,dim_v,init_w2v_att,att,normalize_att,
            seenclass,unseenclass,
            lambda_,
            trainable_w2v,normalize_V=False,normalize_F=True,is_conservative=True,
            uniform_att_1=uniform_att_1,uniform_att_2=uniform_att_2,
            prob_prune=prob_prune,desired_mass=desired_mass, is_conv=False,
            is_bias=True)
model_czsl.to(device)
model_czsl.load_state_dict(torch.load('saved_model/CUB_MSDN_CZSL.pth'))




print('-'*30)
acc_seen, acc_novel, H, _ = eval_zs_gzsl(dataloader,model_gzsl,device,bias_seen=-bias,bias_unseen=bias)
_, _, _, acc_zs = eval_zs_gzsl(dataloader,model_czsl,device,bias_seen=-bias,bias_unseen=bias)

print('acc_unseen=%.3f, acc_seen=%.3f, H=%.3f, acc_zs=%.3f'%(acc_novel,acc_seen,H, acc_zs))# %%