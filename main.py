import os
import numpy as np
import cv2
import shutil

show_bit_bots_img = False
show_yolo_img = False

class DataSet():
    def __init__(self, images_path, labels_path, dataset_type):
        self.images_path = images_path
        self.labels_path = labels_path
        self.dataset_type = dataset_type

def main():
    src_dir = 'src_dir'
    dst_dir = 'dst_dir'
    src_datasets = []
    dst_dataset_name = 'ball_mrl'

    data_use_cases = ['train', 'test', 'validation']
    dataset_elements = ['images', 'labels']

    dataset_types = ['bit_bots', 'yolo']

    # Find source text file and image directory

    # Iterate on source directory dataset types
    for src_dataset_type in os.listdir(src_dir):
        # print(src_dataset_type)
        if (src_dataset_type not in dataset_types):
            print("unknown dataset type:", src_dataset_type)
            continue

        src_dataset_dir = os.path.join(src_dir, src_dataset_type)
        # Check if it is a directory (then it may be a correct dataset)
        # print(src_dataset_dir)
        if os.path.isdir(src_dataset_dir):
            src_label = None
            src_img_dir = None
            src_label_found = False
            src_img_dir_found = False
            # Iterate on the datasets of this type
            # for src_dataset_item in os.listdir(src_dir_item_url):
            for src_dataset_type_item in os.listdir(src_dataset_dir):
                # Find the text file in the dataset
                # print(src_dataset_type_item)
                src_dataset_item_url = os.path.join(src_dataset_dir, src_dataset_type_item)

                for item in os.listdir(src_dataset_item_url):
                    url_in_dataset = os.path.join(src_dataset_item_url, item)

                    if (src_dataset_type == 'bit_bots'):
                        if os.path.isfile(url_in_dataset) and url_in_dataset.endswith('.txt'):
                            print('labels found')
                            # print('found {0} as the source dataset main txt file'.format(src_dataset_item_url))
                            src_label = url_in_dataset
                            src_label_found = True
                    elif (src_dataset_type == 'yolo'):
                        # print("yolo name::::", url_in_dataset, (url_in_dataset.endswith('labels')))
                        if os.path.isdir(url_in_dataset) and url_in_dataset.endswith('labels'):
                            print('labels found')
                            # print('found {0} as the source dataset main txt file'.format(src_dataset_item_url))
                            src_label = url_in_dataset
                            src_label_found = True

                    if os.path.isdir(url_in_dataset):
                        print('img dir found')
                        src_img_dir = url_in_dataset
                        src_img_dir_found = True

                if src_label_found and src_img_dir_found:
                    dataset = DataSet(src_img_dir, src_label, src_dataset_type)
                    src_datasets.append(dataset)

    if len(src_datasets) == 0:
        print("Could not initialize converting session")
        return

    for dataset in src_datasets:
        print(dataset.images_path, dataset.labels_path, dataset.dataset_type)

    # Create destination directory structure


    # Delete destination directory if exists
    if os.path.exists(dst_dir) and os.path.isdir(dst_dir):
        shutil.rmtree(dst_dir)
    os.makedirs(dst_dir)

    dataset_dir = os.path.join(dst_dir, dst_dataset_name)
    os.makedirs(dataset_dir)

    # Create directory for train, test, and validation splits, and also create images and labels directory for each
    for data_use_case in data_use_cases:
        for dataset_element in dataset_elements:
            dir = os.path.join(dataset_dir, data_use_case, dataset_element)
            os.makedirs(dir)


    # Iterate on source datasets
    data_cnt = 0
    for src_dataset in src_datasets:
        if (src_dataset.dataset_type == 'bit_bots'):
            # Open source text file and iterate on dataset items
            with open(src_dataset.labels_path, 'r') as src_txt_file:
                # Read all lines of the file
                lines = src_txt_file.readlines()
                count = 0

                # Iterate on lines
                for line in lines:
                    count += 1
                    if count <= 6:
                        print("passing")
                        continue

                    # print(line, end = '')
                    info = line.split("|")
                    ball_in_img = False
                    if len(info) == 3:
                        annotation_type, img_file_name, not_in_img = info
                        ball_in_img = False
                    elif len(info) == 12:
                        annotation_type, img_file_name, img_width, img_height, x1, y1, x2, y2, center_x, center_y, width, height = info
                        ball_in_img = True

                    src_img_path = os.path.join(src_dataset.images_path, img_file_name)

                    # Visualize dataset
                    if (show_bit_bots_img):
                        img = cv2.imread(src_img_path)
                        if (ball_in_img):
                            # cv2.rectangle(img, (int(float(x1)), int(float(y1))), (int(float(x2)), int(float(y2))), (0, 0, 255), 1, cv2.LINE_AA)
                            cv2.rectangle(img, (int(float(center_x) - float(width)/2), int(float(center_y) - float(height)/2)), (int(float(center_x) + float(width)/2), int(float(center_y) + float(height)/2)), (0, 0, 255), 1, cv2.LINE_AA)

                        cv2.imshow("ball", img)
                        cv2.waitKey(0)

                    # Create destination text file content
                    dst_content = []
                    if (ball_in_img):
                        label = "0" + " " + str(float(center_x) / float(img_width)) + " " + str(float(center_y) / float(img_height)) + " " + str(float(width) / float(img_width)) + " " + str(float(height) / float(img_height)) + "\n"
                    else:
                        label = "\n"
                    dst_content.append(label)

                    # Fill the destination text file
                    dst_name = 'frame' + str(data_cnt)
                    dst_file_prefix = img_file_name.split(".")[0]
                    dst_txt_file = os.path.join(dataset_dir, data_use_cases[0], dataset_elements[1], dst_name + ".txt")
                    with open(dst_txt_file, 'w') as dest_file:
                        dest_file.writelines(dst_content)
                        dest_file.close()

                    # Copy image
                    img_dst_path = os.path.join(dataset_dir, data_use_cases[0], dataset_elements[0], dst_name + ".jpg")
                    shutil.copyfile(src_img_path, img_dst_path)
                    # # 2nd option
                    # shutil.copy(src, dst)  # dst can be a folder; use shutil.copy2() to preserve timestamp

                    data_cnt += 1

                src_txt_file.close()
        elif (src_dataset.dataset_type == 'yolo'):
            for image in os.listdir(src_dataset.images_path):
                img_path = os.path.join(src_dataset.images_path, image)
                dst_file_prefix = image.split(".")[0]
                image_label_path = os.path.join(src_dataset.labels_path, dst_file_prefix + ".txt")
                with open(image_label_path, 'r') as label_file:
                    lines = label_file.readlines()
                    dst_content = []
                    for line in lines:
                        info = line.split(" ")
                        class_number, x_center, y_center, width, height = info
                        #
                        # Determine BALL_INDEX (maybe by hand)
                        #
                        # print("src:::::::", src_dataset.images_path)
                        if (src_dataset.images_path == "src_dir/yolo/positive-Robocup-2019/images"):
                            BALL_INDEX = 2
                        elif (src_dataset.images_path == "src_dir/yolo/ball-ramtin/images"):
                            BALL_INDEX = 0

                        if (int(class_number) != BALL_INDEX):
                            continue

                        if show_yolo_img:
                            img = cv2.imread(img_path)
                            # print(img.shape)
                            x_center_pixel = float(x_center) * img.shape[1]
                            width_pixel = float(width) * img.shape[1]
                            y_center_pixel = float(y_center) * img.shape[0]
                            height_pixel = float(height) * img.shape[0]
                            cv2.rectangle(img, (int(float(x_center_pixel) - float(width_pixel)/2), int(float(y_center_pixel) - float(height_pixel)/2)),
                                               (int(float(x_center_pixel) + float(width_pixel)/2), int(float(y_center_pixel) + float(height_pixel)/2)),
                                               (0, 0, 255),
                                               1,
                                               cv2.LINE_AA)
                            # cv2.rectangle(img, (int(float(x1)), int(float(y1))), (int(float(x2)), int(float(y2))), (0, 0, 255), 1, cv2.LINE_AA)
                            cv2.imshow("ball", img)
                            cv2.waitKey(0)
                        # Create destination text file content
                        if int(class_number) == BALL_INDEX:
                            label = "0" + " " + str(float(x_center)) + " " + str(float(y_center)) + " " + str(float(width)) + " " + str(float(height)) + "\n"
                            dst_content.append(label)

                    # Fill the destination text file
                    dst_name = 'frame' + str(data_cnt)
                    dst_file_prefix = image.split(".")[0]
                    dst_txt_file = os.path.join(dataset_dir, data_use_cases[0], dataset_elements[1], dst_name + ".txt")
                    with open(dst_txt_file, 'w') as dest_file:
                        if (len(dst_content) == 0):
                            label = "\n"
                            dst_content.append(label)
                        dest_file.writelines(dst_content)
                        dest_file.close()

                    # Copy image
                    img_dst_path = os.path.join(dataset_dir, data_use_cases[0], dataset_elements[0], dst_name + ".jpg")
                    shutil.copyfile(img_path, img_dst_path)
                    # # 2nd option
                    # shutil.copy(src, dst)  # dst can be a folder; use shutil.copy2() to preserve timestamp

                    label_file.close()
                data_cnt += 1
        print(data_cnt)

if __name__ == '__main__':
    main()
