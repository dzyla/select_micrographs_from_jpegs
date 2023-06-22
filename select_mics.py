import cv2
import numpy as np
import easygui
import os
from pathlib import Path

def load_existing_selection():
    try:
        file_holder = set(np.load('selected_images.npy', allow_pickle=True).tolist())
    except FileNotFoundError:
        file_holder = set()
        print('Creating new file for selection')
    return file_holder

def save_selected(file_holder):
    np.save('selected_images.npy', list(file_holder))

def fetch_files_from_folder():
    folder = easygui.diropenbox()
    if folder is None:
        print('No directory chosen, quitting.')
        quit()

    return [str(path) for path in Path(folder).rglob('*.jpg')]

def display_keys_and_intro():
    print('''
    This tool can be used to manually curate the micrographs which were saved as a jpegs during the EPU data collection.

    Important keys:
    Space -> accept micrograph
    n     -> next micrograph
    b     -> previous micrograph
    x     -> remove current micrograph
    i     -> jump by 100 micrographs forward
    u     -> jump by 100 micrographs backwards
    e     -> export selected micrographs to txt file
    ESC   -> Exit program\n
    ''')

def update_display(file_holder, filename, img, slice):
    fontColor = (255, 255, 255) if filename in file_holder else (0, 0, 0)
    cv2.putText(
        img, 
        f'Image {slice}, {filename}', 
        (10, 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        fontColor,
        2
    )
    cv2.imshow('ImageStack', img)

def update_file_holder(key, file_holder, filename, slice, data_size):
    if key == 32:  # Space key
        if filename not in file_holder:
            file_holder.add(filename)
            print(f'Selected {filename}, total files: {len(file_holder)}')
        else:
            print(f'File {filename} is already chosen')
    elif key == ord('n'):
        if slice < data_size - 1:
            slice += 1
    elif key == ord('b'):
        if slice > 0:
            slice -= 1
    elif key == ord('i'):
        if slice < data_size - 101:
            slice += 100
    elif key == ord('u'):
        if slice > 99:
            slice -= 100
    elif key == ord('x'):
        if filename in file_holder:
            file_holder.remove(filename)
            print(f'{filename} removed!')
    elif key == ord('e'):
        export_selection(file_holder)
    return slice, file_holder


def export_selection(file_holder):
    with open('selected_images.txt', 'w') as f:
        for item in file_holder:
            f.write(f"{item.replace('.jpg', '_fractions.mrc')}\n")
    print('Exported txt file')

def main():
    display_keys_and_intro()

    file_holder = load_existing_selection()

    jpg_files = fetch_files_from_folder()

    data_size = len(jpg_files)
    print(f'-->> Already {len(file_holder)} images selected out of {data_size} ({round(len(file_holder)/data_size*100, 3)}%)<<--\n')

    cv2.namedWindow('ImageStack', cv2.WINDOW_NORMAL)

    slice = 0
    while True:
        img = cv2.imread(jpg_files[slice])
        img = cv2.resize(img, (800, 600))

        filename = os.path.basename(jpg_files[slice])

        update_display(file_holder, filename, img, slice)

        k = cv2.waitKey(-1) & 0xFF

        if k == 27:  # ESC
            cv2.destroyAllWindows()
            save_selected(file_holder)
            quit(1)

        slice, file_holder = update_file_holder(k, file_holder, filename, slice, data_size)

if __name__ == "__main__":
    main()