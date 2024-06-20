import os
import numpy as np
from PIL import Image

def matrix_to_image(matrix, output_image_path):
    """
    Converts a matrix to an image and saves it to the specified path.
    """
    matrix = np.array(matrix)
    matrix = matrix * 255  
    image = Image.fromarray(matrix.astype(np.uint8))
    image.save(output_image_path)

def read_matrix_from_file(file_path):
    """
    Reads a matrix from a text file.
    """
    with open(file_path, 'r') as file:
        matrix = []
        for line in file:
            row = [int(val) for val in line.split()]
            matrix.append(row)
    return matrix

def convert_all_matrices_to_images(input_folder, output_folder):
    """
    Converts all matrix text files in the input folder to images and saves them in the output folder.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file_name in os.listdir(input_folder):
        if file_name.endswith('_matrix.txt'):  
            file_path = os.path.join(input_folder, file_name)
            matrix = read_matrix_from_file(file_path)
            output_image_path = os.path.join(output_folder, file_name.replace('_matrix.txt', '.png'))
            matrix_to_image(matrix, output_image_path)
            print(f"Converted {file_path} to {output_image_path}")

if __name__ == "__main__":
    input_folder = "/home/jw38176/gem5/jw38176/results/coremark_logs/radix2" 
    output_folder = "/home/jw38176/gem5/jw38176/results/coremark_logs/radix2" 
    convert_all_matrices_to_images(input_folder, output_folder)
