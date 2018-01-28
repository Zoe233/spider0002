import os

class getData(object):
    '''从yaozhi_dic中获取数据的基类'''

    def __init__(self):
        self.data =[]
        self.data_list=[]

    def __read(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        filepath = os.path.join(base_dir,'yaozh_dic.txt')
        with open(filepath,'r') as f:
            data = f.read()
            self.data_list = data.split('; ')[:-1]
        return self.data_list

    def transform(self):
        self.__read()
        for i in self.data_list:
            self.data.append(eval(i))
        return self.data

if __name__=='__main__':
    g = getData()
    g.transform()
    print(g.data)
    print(len(g.data))





