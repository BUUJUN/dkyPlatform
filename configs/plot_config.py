# -*- encoding: utf-8 -*-
'''
Created on 2024/10/24 16:56:32

@author: BOJUN WANG
'''
#%%
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties, fontManager

font_path_nsimsun = 'fonts/Nsimsun.ttf'
font_path_simhei = 'fonts/SimHei.ttf'
font_path_tnr = 'fonts/Times New Roman.ttf'

# 将字体文件添加到Matplotlib的字体管理器中
fontManager.addfont(font_path_nsimsun)
fontManager.addfont(font_path_simhei)
fontManager.addfont(font_path_tnr)

font_nsimsun = FontProperties(fname=font_path_nsimsun)
font_simhei = FontProperties(fname=font_path_simhei)
font_tnr = FontProperties(fname=font_path_tnr)

#%%