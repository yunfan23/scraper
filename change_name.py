
from os import listdir
from os import rename
from os.path import isfile, join

working_dir = "/Users/yunfan/Google Drive/assignment-2-kevins00/dataset/cars_v2/audi/"

onlyfiles = [f for f in listdir(working_dir) if isfile(join(working_dir, f))]
for idx, file in enumerate(onlyfiles):
    rename(join(working_dir,file), join(working_dir, "{:03d}.jpg".format(idx)))