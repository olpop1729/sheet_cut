

import pandas as pd

class offset:
    fm45 = 0.0
    fp45 = 0.0

class eProfile:

    def __init__(self):
        self.limb_len = 0
        self.hole_list = []
        self.k = 0
        self.steplap_distance = 0
        self.len_list = []
        self.layers = 1
        self.pattern_len = 0
        self.steplap_count = 0
        self.open = False
        self.x = 0


    def get_x(self):
        try:
            x = int(input('Enter scrap-length : '))
            self.x = x
        except ValueError as err:
            print(err)


    def gen_steplap_vector(self):
        n = self.steplap_count // 2
        d = self.steplap_distance
        if self.steplap_count % 2 == 0:
            self.steplap_vector = [i*d for i in range(n , -n-1, -1) if n != 0]
        else:
            self.steplap_vector = [i*d for i in range(n , -n-1, -1)]

        if self.open:
            return
        else:
            self.steplap_vector = self.steplap_vector[::-1]


    def gen_hole_list(self):
        ll = self.len_list
        ret = []
        for i in range(len(ll) - 1):
            ret.append(sum(ll[:i+1]))
        self.hole_list = ret



    def create_dict(self):
        #d = self.steplap_distance
        n = self.steplap_count
        dn = self.steplap_vector
        m = self.layers
        hl = self.hole_list
        x = self.x
        l = sum(self.len_list)
        exe = []
        vtv = 0
        for i in range(n * m):

            vtv = sum(2*dn[:(i//m)]) + (i//m) * (l + 2*x)

            if len(hl) > 0:
                for j in hl:
                    exe.append(['h', vtv + j + x + dn[(i//m)], 0])
            exe.append(['v', vtv, x])
            exe.append(['fp45', vtv - x, 0])
            exe.append(['fm45', vtv + x, 0])

        self.exe = exe
        self.pl = ( l + 2*x ) * m * n



    def execute(self):
        exe = self.exe
        pl = self.pl

        for i in exe:
            if i[0] in ['fm45']:
                i[1] += 4335 + offset.fm45
            elif i[0] in ['fp45']:
                i[1] += 4335 + offset.fp45
            elif i[0] == 'h':
                i[1] += 1250
            elif i[0] == 0:
                i[1] += 0

        term = 200

        feed = []
        operation = []
        vaxis = []

        while term > 0:
            term -= 1
            cc = min([i[1] for i in exe])
            repeat = False
            for i in exe:
                if i[1] == cc:
                    vaxis.append(i[2])
                    operation.append(i[0])
                    if repeat:
                        feed.append(0)
                    else:
                        feed.append(cc)
                        repeat = True

                    i[1] = pl

                else:
                    i[1] -= cc


        cut_feed = list(zip(feed, vaxis,operation))
        df = pd.DataFrame(data = cut_feed, columns=['Feed','V-Axis','Operation'])
        df.index += 1
        temp = pd.ExcelWriter('../cut_program_output/scrap_0.xlsx')
        df.to_excel(temp)
        temp.save()





    def get_open(self):
        try:
            opn = input('Open ? : ').lower()
            if opn in ['y', 'yes', '1']:
                self.open = True
            elif opn in ['n', 'no', '0']:
                self.open = False
            else:
                print('Assuming false input')
                self.open = False
        except Exception as e:
            print(e)



    def get_layers(self):
        try:
            layers = int(input('Enter no. of layers : '))
            self.layers = layers
        except ValueError as err:
            print(err)


    def get_steplap_distance(self):
        try:
            dist = float(input('Enter steplap distance : '))
            self.steplap_distance = dist
        except ValueError as err:
            print(err)


    def get_len_list(self):
        try:
            l = [float(i) for i in input("Enter L's seperated by spaces : ").split()]
            self.len_list = l
        except ValueError as err:
            print(err)


    def get_steplap_count(self):
        try:
            count = int(input('Enter steplap count : '))
            self.steplap_count = count
        except ValueError as err:
            print(err)


    def __repr__(self):
        return 'Object representation to be implemented'




if __name__ == '__main__':
    a = eProfile()

    a.get_open()
    a.get_x()
    a.get_len_list()
    a.gen_hole_list()
    a.get_steplap_distance()
    a.get_steplap_count()
    a.get_layers()
    a.gen_steplap_vector()
    a.create_dict()
    a.execute()
