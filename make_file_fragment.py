import random
import struct
import os

unit = 4096
file_name = random.sample(range(1, 500000), 499999)


def make_png_dataset():
    '''
        Input : 일반 png 파일
    '''
    folder =er 'C:\\Users\\KimJaeHeon.LAPTOP-BSUIT67J\\Desktop\\png'
    count = 0

    for (path, dirs, files) in os.walk(folder):
        for file in files:
            with open(path + '\\' + file, 'rb') as opened_file:
                png_data = opened_file.read()
                
                while(True):
                    if b'IDAT' not in png_data:
                        break

                    IDAT_sig_index = png_data.find(b'IDAT')
                    if png_data[IDAT_sig_index - 4:IDAT_sig_index - 2] != b'\x00\x00':    # IDAT가 IDAT chunk의 header부분의 시그니처가 아닌 그냥 데이터 부분에 들어있는 값인 경우
                        png_data = png_data[IDAT_sig_index + 4:]
                        continue

                    data_size = cal_size(png_data[IDAT_sig_index - 4:IDAT_sig_index])
                    data_size -= 36    # 압축 시그니처가 들어가는 것을 방지하기 위함
                    png_data = png_data[IDAT_sig_index + 4 + 36:]

                    fragment_num = data_size // unit
                    for i in range(fragment_num):
                        fragment_index = i * unit

                        with open('C:\\Users\\KimJaeHeon.LAPTOP-BSUIT67J\\Desktop\\png_fragment_trainingset\\' + str(file_name[count]), 'wb') as output:
                            output.write(png_data[fragment_index:fragment_index + unit])
                        count += 1



def make_jpg_dataset():
    '''
        Input : 일반 jpg 파일
    '''
    folder = 'D:\\testset\\jpg\\'
    count = 0

    for (path, dirs, files) in os.walk(folder):
        for file in files:
            with open(path + '\\' + file, 'rb') as opened_file:
                jpg_data = opened_file.read()

                scanstart_index = jpg_data.find(b'\xFF\xDA\x00\x0C\x03\x01')
                if scanstart_index < 0:
                    continue

                jpg_data = jpg_data[scanstart_index + 14 + 72:]    # 14 : scanstart size, 72 : scanData에 압축 헤더가 들어가있는 상황 대비 용도

                fragment_num = len(jpg_data) // unit
                for i in range(fragment_num - 1):    # EOIMarker가 포함되어있는 fragment는 drop
                    fragment_index = i * unit

                    with open('D:\\testset\\jpg_fragment_testset\\' + str(file_name[count]), 'wb') as output:
                        output.write(jpg_data[fragment_index:fragment_index + unit])
                    count += 1


def make_h264_dataset():
    '''
        Input : ffmpeg를 사용하여, mp4에서 추출한 h264 파일
    '''
    folder = 'h264s\\'
    signature = b'\x00\x00\x00\x02\x09\xF0'
    count = 0

    for (path, dirs, files) in os.walk(folder):
        for file in files:
            with open(path + '\\' + file, 'rb') as opened_file:
                h264_data = opened_file.read()
                index1 = 0

                while True:
                    index1 = h264_data.find(signature, index1)
                    index2 = h264_data.find(signature, index1 + 6)
                    if index2 < 0:
                        break

                    sample_size = index2 - index1
                    if sample_size < 10000:    # 10000bytes 이상인 sample들을 대상으로만 조각을 만듬. (10000으로 정한건 큰 의미는 없음.)
                        index1 = index2
                        continue

                    start_index = index1 + 256    # 각 sample마다 시작부분에 b'\x00\x00\x00\x02\x09\xF0 ...' 동일한 시그니처가 나타남. 제대로 학습시키기 위하여 시그니처로부터 256bytes 뒤부터 조각을 만듬.
                    fragment_num = (sample_size - 256) // unit
                    for i in range(fragment_num - 1):
                        fragment_index = i * unit

                        with open('h264s_fragment_datasets\\' + str(file_name[count]), 'wb') as output:
                            output.write(h264_data[start_index + fragment_index:start_index + fragment_index + unit])
                        count += 1

                    index1 = index2


def make_h264_dataset2():
    '''
        Input : h264로 인코딩된, 비디오 데이터만 존재하는 mp4 파일 (youtube-dl로 받은 파일)
    '''
    folder = 'D:\\testset\\h264\\'
    count = 0

    for (path, dirs, files) in os.walk(folder):
        for file in files:
            with open(path + '\\' + file, 'rb') as opened_file:
                mp4_data = opened_file.read()
                max_index = len(mp4_data) - 1

                moof_sig_index = mp4_data.find(b'moof')
                box_size = cal_size(mp4_data[moof_sig_index - 4:moof_sig_index])
                mdat_sig_index = moof_sig_index + box_size

                while True:
                    trun_sig_index = mp4_data.find(b'trun', moof_sig_index)
                    sample_count = cal_size(mp4_data[trun_sig_index + 8:trun_sig_index + 12])
                    entry_start_offset = trun_sig_index + 16
                    sample_index = mdat_sig_index + 4

                    for i in range(sample_count):
                        offset = i * 12

                        sample_size = cal_size(mp4_data[entry_start_offset + offset:entry_start_offset + offset + 4])
                        fragment_num = (sample_size - 256) // unit
                        if fragment_num > 0:
                            start_index = sample_index + 256
                            for j in range(fragment_num):
                                fragment_index = j * unit

                                with open('D:\\testset\\\h264_fragment_testset\\' + str(file_name[count]), 'wb') as output:
                                    output.write(mp4_data[start_index + fragment_index:start_index + fragment_index + unit])
                                count += 1

                        sample_index += sample_size

                    box_size = cal_size(mp4_data[mdat_sig_index - 4:mdat_sig_index])
                    moof_sig_index = mdat_sig_index + box_size
                    if moof_sig_index > max_index:
                        break

                    box_size = cal_size(mp4_data[moof_sig_index - 4:moof_sig_index])
                    mdat_sig_index = moof_sig_index + box_size


def make_av1_dataset():
    '''
        Input : av1으로 인코딩된, 비디오 데이터만 존재하는 mp4 파일 (youtube-dl로 받은 파일)
    '''
    folder = 'D:\\testset\\av1\\'
    count = 0

    for (path, dirs, files) in os.walk(folder):
        for file in files:
            with open(path + '\\' + file, 'rb') as opened_file:
                mp4_data = opened_file.read()
                max_index = len(mp4_data) - 1

                moof_sig_index = mp4_data.find(b'moof')
                box_size = cal_size(mp4_data[moof_sig_index - 4:moof_sig_index])
                mdat_sig_index = moof_sig_index + box_size

                while True:
                    trun_sig_index = mp4_data.find(b'trun', moof_sig_index)
                    sample_count = cal_size(mp4_data[trun_sig_index + 8:trun_sig_index + 12])
                    entry_start_offset = trun_sig_index + 16
                    sample_index = mdat_sig_index + 4

                    for i in range(sample_count):
                        offset = i * 8

                        sample_size = cal_size(mp4_data[entry_start_offset + offset:entry_start_offset + offset + 4])
                        fragment_num = (sample_size - 256) // unit
                        if fragment_num > 0:
                            start_index = sample_index + 256
                            for j in range(fragment_num):
                                fragment_index = j * unit

                                with open('D:\\testset\\av1_fragment_testset\\' + str(file_name[count]), 'wb') as output:
                                    output.write(mp4_data[start_index + fragment_index:start_index + fragment_index + unit])
                                count += 1

                        sample_index += sample_size

                    box_size = cal_size(mp4_data[mdat_sig_index - 4:mdat_sig_index])
                    moof_sig_index = mdat_sig_index + box_size
                    if moof_sig_index > max_index:
                        break

                    box_size = cal_size(mp4_data[moof_sig_index - 4:moof_sig_index])
                    mdat_sig_index = moof_sig_index + box_size


def make_h265_dataset():
    '''
        Input : h265 코덱을 사용하는 mp4, https://www.elecard.com/videos에서 받은 특정 파일들만 대상으로 작동
    '''
    folder = 'D:\\testset\\h265\\'
    count = 0

    for (path, dirs, files) in os.walk(folder):
        for file in files:
            with open(path + '\\' + file, 'rb') as opened_file:
                mp4_data = opened_file.read()

                stsz_sig_index = 0
                while True:
                    stsz_sig_index = mp4_data.find(b'stsz', stsz_sig_index + 1)
                    if mp4_data[stsz_sig_index - 4:stsz_sig_index - 2] == b'\x00\x00':
                        break

                sample_count = cal_size(mp4_data[stsz_sig_index + 12:stsz_sig_index + 16])

                entry_size_start_index = stsz_sig_index + 16
                sample_index = 40
                for i in range(sample_count):
                    entry_size_index = i * 4

                    sample_size = cal_size(mp4_data[entry_size_start_index + entry_size_index:entry_size_start_index + entry_size_index + 4])

                    fragment_num = (sample_size - 256) // unit
                    if fragment_num > 0:
                        print(sample_index)
                        start_index = sample_index + 256
                        for j in range(fragment_num - 1):
                            fragment_index = j * unit

                            with open('D:\\testset\\h265_fragment_testset\\' + str(file_name[count]), 'wb') as output:
                                output.write(mp4_data[start_index + fragment_index:start_index + fragment_index + unit])
                            count += 1

                    sample_index += sample_size


def make_wav_dataset():
    '''
        Input : 일반 wav 파일
    '''
    folder = 'D:\\dataset\\wav\\'
    signature = b'\x64\x61\x74\x61'    #wav의 data 시그니처
    count = 0

    for (path, dirs, files) in os.walk(folder):
        for file in files:
            with open(path + '\\' + file, 'rb') as opened_file:
                wav_data = opened_file.read()
                index1 = 0

                index1 = wav_data.find(signature, index1)
                sample_size = int(wav_data[index1+4]) | int(wav_data[index1+5]) << 8 | int(wav_data[index1+6]) << 16 | int(wav_data[index1+7]) << 24
                if sample_size < 10000:    # 10000bytes 이상인 sample들을 대상으로만 조각을 만듬. (10000으로 정한건 큰 의미는 없음.)
                    continue
                start_index = index1
                fragment_num = (sample_size) // unit
                for i in range(fragment_num - 1):
                    fragment_index = i * unit

                    with open('D:\\dataset\\wav_fragment_datasets\\' + str(file_name[count]), 'wb') as output:
                        output.write(wav_data[start_index + fragment_index:start_index + fragment_index + unit])
                    count += 1


def make_m4a_dataset():
    '''
        Input : h265 코덱을 사용하는 mp4, https://www.elecard.com/videos에서 받은 특정 파일들만 대상으로 작동
    '''
    folder = 'D:\\testset\\h265\\'
    count = 0

    for (path, dirs, files) in os.walk(folder):
        for file in files:
            with open(path + '\\' + file, 'rb') as opened_file:
                mp4_data = opened_file.read()

                stsz_sig_index = 0
                while True:
                    stsz_sig_index = mp4_data.find(b'stsz', stsz_sig_index + 1)
                    if mp4_data[stsz_sig_index - 4:stsz_sig_index - 2] == b'\x00\x00':
                        break

                sample_count = cal_size(mp4_data[stsz_sig_index + 12:stsz_sig_index + 16])

                entry_size_start_index = stsz_sig_index + 16
                sample_index = 40
                for i in range(sample_count):
                    entry_size_index = i * 4

                    sample_size = cal_size(mp4_data[entry_size_start_index + entry_size_index:entry_size_start_index + entry_size_index + 4])

                    fragment_num = (sample_size - 256) // unit
                    if fragment_num > 0:
                        print(sample_index)
                        start_index = sample_index + 256
                        for j in range(fragment_num - 1):
                            fragment_index = j * unit

                            with open('D:\\testset\\h265_fragment_testset\\' + str(file_name[count]), 'wb') as output:
                                output.write(mp4_data[start_index + fragment_index:start_index + fragment_index + unit])
                            count += 1

                    sample_index += sample_size


def cal_size(val):
    return struct.unpack('>I', val)[0]


if __name__=='__main__':
    make_png_dataset()
    # make_jpg_dataset()
    # make_h264_dataset()
    # make_h264_dataset2()
    # make_h265_dataset()
    # make_av1_dataset()
    # make_wav_dataset()
