def vb_encode(docIDs):
    bytestream=[]
    for num in docIDs:
        bytes_split = []
        one_bytestream=''
        while True:
            bytes_split.append((num % 128))
            if num < 128:
                break
            else:
                num = int(num/128)
        bytes_split = bytes_split[::-1]
        for i in range(len(bytes_split)):
            if i == len(bytes_split) - 1:
                bytestream.append(bytes([bytes_split[i]+128]))
            else:
                bytestream.append(bytes([bytes_split[i]]))
    return bytestream


def vb_decode(bytestream):
    docIDs = []
    num = 0
    for i in range(len(bytestream)):
        if ord(bytestream[i]) > 127:
            num *= 128
            num += ord(bytestream[i]) - 128
            docIDs.append(num)
            num = 0
        else:
            num *= 128
            num += ord(bytestream[i])
    return docIDs

def print_vb_code(bytestream):
    bytes_print = ''
    for i in range(len(bytestream)):
        num = ord(bytestream[i])
        one_bytestream = ''
        for j in range(8):
            one_bytestream += str(num % 2)
            num = int(num/2)
        bytes_print += one_bytestream[::-1]
        bytes_print += ' '
    print(bytes_print)

