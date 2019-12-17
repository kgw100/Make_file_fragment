import sys
import os 
import struct
# import random
# out_file_name = random.sample(range(1, 10000), 9999)

hwp_sig = '48575020446f63756d656e742046696c65'
RootEntry_sig = '52006f006f007400\
200045006e007400720079'
Section_sig = '530065006300740069006f006e'
bbat_lst = [] #한글 파일 복구 시 사용
error_case1 = 'feffffff'
error_case2 = 'ffffffff'

# 진행 상황 알려줌 
def printProgressBar (iteration,line, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):

    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if line == True and iteration == total: 
        print()

# little Endian으로 정렬된 4byte를 읽어서 Size 계산하기 
def LTE_get_size(hex_lst,index):
    mov_number = 0
    byte_size = 0
    # Get little endian byte size 
    for x in range(4):
        length_byte  = str(format(hex_lst[index+x],'02x')) #legnth_byte는 byte Size를 나타내는 바이트
        byte_size += int(length_byte[0],16)*pow(16,mov_number+1)+\
                    (int(length_byte[1],16)*pow(16,(mov_number)))
        mov_number+= 2
    return byte_size
def get_block_offset(block_num):
    block_offset = (block_num+1) * 512 # -1번째 블록부터 시작하므로
    return block_offset
# def LTE_cal_size(val):
#     return struct.unpack('<I', val)[0] # <I는 BIG endian으로 처리하기 위해서
#                                        # unpack은 tupple로 반환되므로, [0]지정해야함
def check(byte):
    if len(byte) != 0:
        return ord(byte)
    else:
        return 0       
# HWP 파일 헤더를 확인한다. 
def check_ole_filesig(byte, cur_str):
    hex_byte = format(byte,'02x') # 10진수-> 16진수
    if hex_byte == '48':   cur_str = '48' 
    elif hex_byte == '57': cur_str += '57'
    elif hex_byte == '50': cur_str += '50'
    elif hex_byte == '20': cur_str += '20'
    elif hex_byte == '44': cur_str += '44'
    elif hex_byte == '6f': cur_str += '6f'
    elif hex_byte == '63': cur_str += '63'
    elif hex_byte == '75': cur_str += '75'
    elif hex_byte == '6d': cur_str += '6d'
    elif hex_byte == '65': cur_str += '65'
    elif hex_byte == '6e': cur_str += '6e'
    elif hex_byte == '74': cur_str += '74'
    elif hex_byte == '20': cur_str += '20'
    elif hex_byte == '46': cur_str += '46'
    elif hex_byte == '69': cur_str += '69'
    elif hex_byte == '6c': cur_str += '6c'
    elif hex_byte == '65': cur_str += '65'     
    else:
        cur_str = ''  # 속도 향상과 다음 메타 데이터를 찾기 위한 str 초기화
    return cur_str
def check_RtEn_sig(hex_lst, index):
    cur_str = ''
    Root_Entry = False
    for x in range(0,19):
        cur_str += format(hex_lst[index+x],'02x') # 10진수-> 16진수 
    # print(cur_str)
    if cur_str == RootEntry_sig:
        print("Find! RootEntry")
        Root_Entry = True
    else :
        print("No! RootEntry")
        Root_Entry = False
    return Root_Entry
def check_Sect_sig(byte, cur_str):
    hex_byte = format(byte,'02x') # 10진수-> 16진수
    if hex_byte == '53':   cur_str = '53' 
    elif hex_byte == '00': cur_str += '00'
    elif hex_byte == '65': cur_str += '65'
    elif hex_byte == '63': cur_str += '63'
    elif hex_byte == '74': cur_str += '74'
    elif hex_byte == '69': cur_str += '69'
    elif hex_byte == '6f': cur_str += '6f'
    elif hex_byte == '6e': cur_str += '6e'  
    else:
        cur_str = ''  # 속도 향상과 다음 메타 데이터를 찾기 위한 str 초기화   
    return cur_str

def get_BBAT_list(hex_lst,bbat_cnt):
    for x in range(0,bbat_cnt*4,4):
       bbat_lst.append(LTE_get_size(hex_lst, 76+x))
    print(bbat_lst)
def verify_fragment(byte, cur_str):
    if byte == 255:   cur_str += 'ff' 
    elif byte == 254: cur_str += 'fe'
    else : cur_str = ''
    return cur_str

def make_hwp_dataset(input_path,out_path, file_num, frag_cnt_StrNum):
    count = frag_cnt_StrNum # file이름 시작 번호
    error_frag_cnt = 0
    printProgressBar(0,True,file_num+1, prefix = 'Main Process:', suffix = 'Complete', length = 50)
    for file_name in range(1,file_num+1): # 최상위로 가야할 반복문
        hex_lst = []
        cur_str = ''       
        in_filename = input_path+r"\%d.hwp"% (file_name) 
        # print(in_filename)
        try:
            with open(in_filename, "rb") as f:
                            byte = f.read(1)
                            while byte:
                                hex_lst.append(check(byte))
                                byte = f.read(1)  # 바이트가 끝날 때 까지 읽기
                            cur_str = ''
                            hex_lst_len = len(hex_lst)
                            Section_num = 0
                            Section_index = 0
                        
                            temp = 1 #Section num이 두 개가 중복 될 때 처리해주기 위한 변수 , 이전 Section num을 저장한다.
                            print()
                            # printProgressBar(0, False, hex_lst_len, prefix = 'Sub Process:', suffix = '', length = 30)
                            for hex_index in range(hex_lst_len):
                                    cur_str = check_Sect_sig(hex_lst[hex_index], cur_str)
                                    if cur_str == Section_sig :  
                                        Section_num = hex_lst[hex_index+2] # S.e.c.t.i.o.n.[NUM]의 자리 현재 S부터 n까지 읽었으므로 2를 더해준다. 
                                        if Section_num == temp :
                                                hex_index = hex_lst_len  #상태바 표시를 위한 세팅
                                                break
                                        temp = hex_lst[hex_index+2]
                                        Section_index = hex_index - 12 # Section을 찾은 인덱스 , sig값이 13글자이므로 초기로 돌아가기 위해 12앞으로  
                                        # print("Find! Section!")
                                        # print("Section index : %d"%Section_index)                     
                                        # for y in range(4): #검증 
                                        #     print(hex_lst[Section_num+120+y])
                                        Section_StrBlock_num = LTE_get_size(hex_lst,Section_index+116)
                                        Section_StrBlock_index = get_block_offset(Section_StrBlock_num)
                                        Section_size = LTE_get_size(hex_lst, Section_index+120) #size number start+120   
                                        # print("Section_size: %02x"%Section_size) 
                                        frag_cnt = Section_size//4096 ## fragment가 몇개가 나오는지 구하기 
                                        if Section_StrBlock_index > hex_lst_len: # Section 정보가 깨져서 전체파일크기보다 큰 값이 들어가는 경우 예외처리
                                            temp = 1 # 현재 찾은 Section Num이 잘못됐으므로 같은 Num의 정상적인 Section 을 찾기 위해 초기 세팅
                                            continue
                                        if frag_cnt != 0 : # fragment 크기가 4096보다 작지않을 때 == BBAT가 존재하는 
                                            for frag_mov in range(0,4096*frag_cnt,4096):
                                                error_flag = False
                                                save_file_name = out_path +(r'\%d'%(count+1))
                                                f.seek(Section_StrBlock_index+frag_mov)
                                                data = f.read(4096)                                                                                         
                                                #검증                
                                                if len(data) < 4096 : 
                                                    #드문 경우로 4096바이트보다 적은 경우 수가 존재
                                                    continue
                                                varify_data = bytearray(data)
                                                for x in range(4096):
                                                    cur_str = verify_fragment(varify_data[x],cur_str)
                                                    if cur_str == error_case1 or cur_str == error_case2:
                                                        error_flag = True
                                                        error_frag_cnt += 1
                                                        break                                     
                                                if error_flag == True :
                                                    #간혹 낮은 버전에서 Entry정보나 부가정보가 빨려들어가는 경우 
                                                    continue    
                                                with open(save_file_name, 'wb') as out:
                                                    out.write(data) # print(data, file=save_file) 이렇게 하면 인코딩이 잘못됨            
                                                count += 1
                                            hex_index = hex_lst_len
                                        else :
                                            # print("Section size is small!")
                                            hex_index = hex_lst_len #상태바 표시를 위한 세팅
                                            break
                                        printProgressBar(hex_index, False, hex_lst_len, prefix = 'Sub Process:', suffix = '', length = 20)
            # print("file end!")
            print()
            printProgressBar(file_name+1, True, file_num+1, prefix = 'Main Process:', suffix = 'Complete', length = 50)
        except:
            continue
    print("에러 파일 조각 : %d"% error_frag_cnt)
    print("제거 완료!")

if __name__ == "__main__":
    input_path = r'D:\hwp_originfile2' #원본 파일 경로 
    file_num = 670 # 원본 한글 파일 개수
    count = 43112 # output_filename count
    out_path = r'D:\hwp_fragment_datasets' #파일 조각 저장 경로 
    make_hwp_dataset(input_path,out_path,file_num,count)
    