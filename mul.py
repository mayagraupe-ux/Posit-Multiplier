import math



class Posit():
    def __init__(self, N = None, es=None, value=0):
        if( N != None and es != None):
            self.N = N
            self.es = es
        else:
            self.N = 8
            self.es = 0
        
        self.value = 0
        self.numPat = 2**self.N  #num of bit patterns
        self.useed = 2**2**self.es #useed value

        self.maxpos = 2**(4*self.N - 8)
        self.minpos = 1/self.maxpos

        self.zero = 0
        self.inf = 2** (self.N - 1)


        ##implemente quire


def mul(self, other):
    #make sure both are posits
    if type(other) != Posit:
        other = Posit(self.N, self.es, other)
    
    #check for 0 and inf
    if(self.value == 0 or other.value == 0):
        return Posit(self.N, self.es, 0)
    if(self.value == self.inf or other.value == other.inf):
        return Posit(self.N, self.es, self.inf)
    

    
    
    #extract components
   
    sign_a, regime_a, exponent_a, fraction_a = self.extract()
    sign_b, regime_b, xponent_b, fraction_b = other.extract()

    #multiply and get scale

    fraction_product = fraction_a * fraction_b
    scale_product = 2**(self.es) * (regime_a + regime_b) + exponent_a + exponent_b
    sign_product = sign_a ^ sign_b

    #see if overflow in fraction product

    fa = math.floor(math.log2(fraction_a))
    fb = math.floor(math.log2(fraction_b))
    fc = math.floor(math.log2(fraction_product))

    # adjust scale if there was overflow in the product
    #use logs to find out how many bits were in each input, and how many bits are in the product
    #if they don't match, theres overflow

    scale_product += fc - (fa  + fb)

    #construct posit
    return self.construct(sign_product, scale_product, fraction_product)



def extract(self):
    #returns sign, regime, exponent, fraction
    x = self.value

    #check excpetion values
    if(x == 0):
        return 0, 0, 0, 0
    if(x == self.inf):
        return None
    
    #get sign by checking msb
    sign = checkBit(x, self.N - 1)

    #get regime by counting leading bits
    regime_count = 0

    #if sign is 1, count leading 1s and subtract 1, else count leading 0s and make neg
    if(sign == 1):
        while(checkBit(x, self.N - 2 - regime_count) == 1 and regime_count < self.N - 1):
            regime_count += 1
        regime_count -= 1
    else:
        while(checkBit(x, self.N - 2 - regime_count) == 0 and regime_count < self.N - 1):
            regime_count += 1
        regime_count = -regime_count
    #still have to account for terminating bit
    
    #get exponent by shifting out regime and sign bits
    exp_length = max(0, min(self.es, self.N - 1 - abs(regime_count)))
    exp = extractBits(x, self.N - 1 - abs(regime_count) - exp_length, exp_length)

    #get fraction by shifting out regime, exponent, and sign bits
    fraction_length = max(0, self.N - 1 - abs(regime_count) - exp_length)
    fraction = removeTrailingZeros(setBit(extractBits(x, 0, fraction_length), fraction_length))

    return sign, regime_count, exp, fraction



    





def construct(self, sign, scale, fraction):
    print("weeee")
    pass


#helper function to check if a bit is a 1 or 0
def checkBit(value, bit):
    return (value >> bit) & 1

def extractBits(value, start, length):
    mask = (1 << length) - 1
    return (value >> start) & mask

def setBit(value, bit):
    return value | (1 << bit)

def removeTrailingZeros(value):
    while value > 0 and (value & 1) == 0:
        value >>= 1
    return value