def vb_encode(docIDs):
    bytestream = ''
    for num in docIDs:
        bytes_split = []
        one_bytestream=''
        while True:
            bytes_split.append((num % 128))
            if num < 128:
                break
            else:
                num = int(num/128)
        for i in range(len(bytes_split)):
            for j in range(7):
                one_bytestream += str(bytes_split[i] % 2)
                bytes_split[i] = int(bytes_split[i] / 2)
            if i == 0:
                one_bytestream += '1'
            else:
                one_bytestream += '0'
        bytestream += one_bytestream[::-1]
    return bytestream


def vb_decode(bytestream):
    docIDs = []
    num = 0
    while len(bytestream) > 0:
        one_byte = bytestream[0:8]
        bytestream = bytestream[8:len(bytestream)]
        for i in range(1, 8):
            num *= 2
            num += int(one_byte[i])
        if one_byte[0] == '1':
            docIDs.append(num)
            num = 0
    return docIDs


