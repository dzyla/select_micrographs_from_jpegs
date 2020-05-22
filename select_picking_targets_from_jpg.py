import cv2
import numpy as np
import glob
import easygui
import os

msg = '''
This tool can be used to manually curate the micrographs which were saved as a jpegs during the EPU data collection.

To use it please follow this:
1) Copy all jpegs into the single folder
2) Run the script (double click on it or from command line)
3) Enjoy selecting micrographs! '''

print('''
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

'''Script saves automatically the selection as a numpy file (*.npy). You can start and stop picking, 
and your selection will be saved.

Black labels mean that the micrograph is not yet selected, white ones that it is already selected.
'''


def save_selected(holder):
    holder = np.stack(holder)
    np.save('selected_images.npy', holder)


def show_files():
    try:
        file_holder = np.load('selected_images.npy', allow_pickle=True)
        np.save('selected_images_bak.npy', file_holder)

        file_holder = file_holder.tolist()

    except:
        file_holder = []
        print('Opening new file for selection')

    # Open jpg folder
    folder = easygui.diropenbox()
    try:
        jpg_files = glob.glob(folder + '\\*.jpg')
        data_size = len(jpg_files)
        print('-->> already {} images selected out of {} ({}%)<<--\n'.format(len(file_holder), data_size, round(len(file_holder)/data_size*100, 3)))

    except:
        print('No directory chosen, quitting.')
        quit()


    cv2.namedWindow('ImageStack')
    cv2.namedWindow('ImageStack', cv2.WINDOW_NORMAL)

    # starting slice
    slice = 0

    while (1):
        num = len(file_holder)

        # slice = cv2.getTrackbarPos('Particle', 'ImageStack')

        img = cv2.imread(jpg_files[slice])

        font = cv2.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = (10, 10)
        fontScale = 0.5
        lineType = 2

        filename = os.path.basename(jpg_files[slice])

        # change the label color
        if filename not in file_holder:
            fontColor = (0, 0, 0)

        else:
            fontColor = (255, 255, 255)

        text_to_show = 'Image {}, {}'.format(slice, filename)
        img = cv2.resize(img, (800, 600))

        cv2.putText(img, text_to_show,
                    bottomLeftCornerOfText,
                    font,
                    fontScale,
                    fontColor,
                    lineType)

        cv2.imshow('ImageStack', img)
        cv2.namedWindow('ImageStack', cv2.WINDOW_NORMAL)

        k = cv2.waitKey(-1) & 0xFF

        # ESC
        if k == 27:
            cv2.destroyAllWindows()
            quit(1)

        # Space
        elif k == 32:
            if filename not in file_holder:

                # print(filename, file=fh)
                print('Selected {}, total files: {}'.format(filename, num))
                file_holder.append(filename)
                save_selected(file_holder)

            else:
                print('File already chosen!')

        # n
        elif k == 110:
            if slice < data_size - 1:
                slice += 1

        # jump by 100
        elif k == ord('i'):
            if slice < data_size - 1 - 100:
                slice += 100

        # jump by -100
        elif k == ord('u'):
            if slice >= 100:
                slice -= 100

        # b, jump by 1
        elif k == 98:
            if slice > 0:
                slice -= 1

        # x
        elif k == ord('x'):
            if filename in file_holder:
                file_holder.remove(filename)
                print('{} removed!'.format(filename))
                save_selected(file_holder)

            else:
                print('{} File not selected yet'.format(filename))

        # Export data to txt
        elif k == ord('e'):
            with open('selected_images.txt', 'w') as f:
                for item in file_holder:
                    # change the final MRC file output so it maches later
                    f.write("%s\n" % item.replace('.jpg', '_fractions.mrc'))
            print('Exported txt file')


show_files()
