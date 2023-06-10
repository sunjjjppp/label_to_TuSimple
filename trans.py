#// --run--
"""
Time: 2022.8.10
Fuction: labelme标注的数据 转 tusimple格式数据集 ,车道线数据集
Author:yu_fang


tusimple格式数据集:
    标注json 文件中每一行包括三个字段 ：
    raw_file : 每一个数据段的第20帧图像的的 path 路径
    lanes 和 h_samples 是数据具体的标注内容，为了压缩，h_sample 是纵坐标（等分确定），lanes 是每个车道的横坐标，是个二维数组。-2 表示这个点是无效的点。
    标注的过程应该是，将图片的下半部分如70%*height 等分成N份。然后取车道线（如论虚实）与该标注线交叉的点

"""
import cv2
import os
import glob
import json
import numpy as np
import shutil

print("[LOG] start ...")
# lebalme标注的文件路径，如：01.jpg,01.json ...
#labelme_dir = "/media/Linux/work/clrnet/Railway_tusimple20220808"
labelme_dir = "/home/sjp/my2tusimple/before/"
#labelme_dir = "/media/Linux/work/clrnet/Railway_tusimple20220808_test"

# 存放tusimple数据集的根目录路径
result_dir = "/home/sjp/my2tusimple/after"
#result_dir = "/media/Linux/work/clrnet/tusimple_self_202208101107_test"

# 保存的json文件名，带后缀，命名类似tusimple数据集里的json文件名
json_file_name = "label_data_0809.json"
# 同时在clips文件夹里子文件命名为0810
clips_sub_name = os.path.splitext(json_file_name)[0].split("_")[-1]
clips_sub = os.path.join("clips",clips_sub_name)
# 判断结果文件路径文件夹是否存在
if not os.path.exists(result_dir):
    os.makedirs(result_dir)
# 创建clips文件夹,及子文件夹
clips_sub_dir = os.path.join(result_dir,clips_sub)
if not os.path.exists(clips_sub_dir):
    os.makedirs(clips_sub_dir)

# 定义h_samples 纵坐标等分区间，根据自己的数据图像调整
h_samples = list(range(0, 1080, 10)) # range（start,end,step）
print("h_sample:",h_samples)

#批量获取图片
labelme_img = glob.glob(labelme_dir+'/*.jpg')  # 根据自己的图片格式更改，这里是*.jpg格式
print("labelme_json:",labelme_img)


# 写入json文件
json_file_path = os.path.join(result_dir,json_file_name)
with open(json_file_path, 'w') as wr:
    # 遍历img,json
    for idx, img_path in enumerate(labelme_img):
        print(idx,img_path)
        img_name_file = os.path.basename(img_path)
        # 获取img名字，去掉后缀
        img_name = os.path.splitext(img_name_file)[0]
        # 获取对应的json文件路径
        json_path = os.path.splitext(img_path)[0] + ".json"
        # 初始化一个list存放单张图的所有车道线
        lanes = []
        dict_img_per = {}
        if os.path.isfile(json_path):
            img = cv2.imread(img_path,-1)
            img_w = img.shape[1]
            img_h = img.shape[0]
            #binary_image = np.zeros([img_h, img_w], np.uint8)

            # 绘制横线h_samples
            binary_image_h = np.zeros([img_h, img_w], np.uint8)
            for h in h_samples:
                cv2.line(binary_image_h,(0,h),(img_w-1,h),(255),thickness=1)
            # cv2.imshow("2",binary_image_h)
            # 加载json文件
            with open(json_path, 'r') as json_obj:
                data = json.load(json_obj)
                for shapes in data['shapes']:
                    binary_image = np.zeros([img_h, img_w], np.uint8)
                    single_lane = []
                    label = shapes['label']
                    # print("label:",label)
                    points = shapes['points']   # 标注的linestrip
                    points = np.array(points, dtype=int)
                    cv2.polylines(binary_image,[points],False,(255),thickness=1) # 绘制车道线
                    img_and = cv2.bitwise_and(binary_image,binary_image_h)
                    # 获取宽高交点
                    for h in h_samples:
                        start = False
                        temp_w = []
                        for w in range(img_w):
                            if img_and[h, w] >= 1:
                                start = True
                                temp_w.append(w)
                        if start:
                            half = len(temp_w) // 2
                            median = (temp_w[half] + temp_w[~half])/2
                            median = int(median)
                            # print("half:",half,median)
                            single_lane.append(median)
                        else:
                            single_lane.append(-2)
                    # print("single_lane:",single_lane)
                    # cv2.imshow("1",img_and)
                    # cv2.waitKey(0)
                    lanes.append(single_lane)
            json_obj.close()
            print("lanes:",lanes)
            raw_file = os.path.join(clips_sub,img_name_file)
            shutil.copy(img_path, clips_sub_dir)
            dict_img_per = {"lanes":lanes,"h_samples":h_samples,"raw_file":raw_file}
            # print("dict_img_per:",dict_img_per)
            # 将dict写入名称为wr的文件中
            # json.dump(dict_img_per, wr, indent=4)  # indent控制间隔,缩进
            json.dump(dict_img_per, wr)
            wr.write('\n')
        else:
            continue
    wr.close()

