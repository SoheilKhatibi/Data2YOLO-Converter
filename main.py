import os
import numpy as np
import cv2
import shutil

show_img = True

def main():
    src_dir = 'src_dir'
    dst_dir = 'dst_dir'
    src_datasets = []
    dst_dataset_name = 'ball_mrl'

    data_use_cases = ['train', 'test', 'validation']
    dataset_elements = ['images', 'labels']


    # Find source text file and image directory

    # Iterate on source directory items
    for src_dataset_dir in os.listdir(src_dir):
        src_dir_item_url = os.path.join(src_dir, src_dataset_dir)
        # Check if it is a directory (then it may be a correct dataset)
        print(src_dir_item_url)
        if os.path.isdir(src_dir_item_url):
            src_txt = None
            src_img_dir = None
            src_txt_found = False
            src_img_dir_found = False
            # Iterate on the dataset directory's items
            for src_dataset_item in os.listdir(src_dir_item_url):
                # Find the text file in the dataset
                src_dataset_item_url = os.path.join(src_dir_item_url, src_dataset_item)
                if os.path.isfile(src_dataset_item_url) and src_dataset_item_url.endswith('.txt'):
                    print('txt found')
                    # print('found {0} as the source dataset main txt file'.format(src_dataset_item_url))
                    src_txt = src_dataset_item_url
                    src_txt_found = True
                elif os.path.isdir(src_dataset_item_url):
                    print('img dir found')
                    src_img_dir = src_dataset_item_url
                    src_img_dir_found = True
            
            if src_txt_found and src_img_dir_found:
                src_datasets.append([src_txt, src_img_dir])

    if len(src_datasets) == 0:
        print("Could not initialize converting session")
        return


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
        # Open source text file and iterate on dataset items
        with open(src_dataset[0], 'r') as src_txt_file:
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

                src_img_path = os.path.join(src_dataset[1], img_file_name)

                # Visualize dataset
                if (show_img):
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



if __name__ == '__main__':
    main()
