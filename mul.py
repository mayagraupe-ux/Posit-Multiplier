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
    
    #need to floor divide scale by 2^es to get regime, and mod by 2^es to get exponent
    regime = scale // (2 ** self.es)
    exponent = scale % (2 ** self.es)

    #num of bits needed for regime - if pos, need +2 to account for terminating
    #if neg, need +1 to account for terminating and make it neg
    if(regime >= 0):
        regime_length = regime + 2
    else:
        regime_length = -regime + 1

    #overflow to maxpos and underflow to minpos 
    if(regime_length > self.N - 1):
            p = Posit(N = self.N, es =self.es)
            p.set_bit_pattern(self.maxpos if regime> 0 else self.minpos)
            if sign ==1:
                p = -p # do i need a 2s comp here?
            return p
    
    #regime
    if regime>=0:
        #calculate how many bits are to the right of the regime block
        shift_amount = self.N - 1 - regime_length

        if(shift_amount >=0):
            n|= createMask(regime_length, shift_amount)
        else: #regime length takes up rest of posit and no terminating bit
            n|= createMask(self.N-1, 0)
    else:
        #when regime < 0, already have 0s in the msb, so just need to set terminating bit
        terminating_bit_position = self.N - 2 - regime_length
        n = setBit(n, terminating_bit_position)
        

    #count how many bits are left for exponent and fraction
    exp_bits = max(0, min(self.es, self.N- 1 - regime_length))
    fraction_bits= max(0, self.N - 1 - regime_length - exp_bits)

    #remove trailing zeros
    fraction = removeTrailingZeros(fraction)
    #subtract 1 from fraction to account for implicit leading 1
    fraction_length = countBits(fraction) -1
    #remove hidden bit
    fraction &= 2**(countBits(fraction)-1) - 1

    #check how many bits left open
    trailing_bits = self.N - 1 - regime_length
    #concatenate exp and frac
    exp_frac = removeTrailingZeros((exponent << fraction_bits) | fraction)

    #min number of bits needed to represent exp and frac
    if fraction_length == 0:
        exp_frac_bits = self.es - countTrailingZeros(exponent)
    else:
        exp_frac_bits = self.es + fraction_length


    #round

    if trailing_bits < exp_frac_bits:
        #get overflow bits
        overflown = exp_frac & createMask(exp_frac_bits - trailing_bits, 0)
        #truncate trailing bits and encode to a number
        n |= exp_frac << (exp_frac_bits - trailing_bits)

        #checking for a tie
        if(overflown == (1 << (exp_frac_bits - trailing_bits -1 ))): # creates a 1 followed by 0s of the length
            #of the overflow to see if it is exactly half (10000)
            #check last bit
            if checkBit(exp_frac, exp_frac_bits - trailing_bits):
                n += 1
        elif (overflown > ( 1 << (exp_frac_bits - trailing_bits))):
           #if greater, round up
            n+=1
        else:
            None

    else:
        n |= exp_frac << (trailing_bits - exp_frac_bits)

    p = Posit(N = self.N, es = self.es)
    #if neg, 2s comp
    if sign == 0:
        p.set_bit_pattern(n)
    else:
        p.set_bit_pattern(twosComp(n, self.N))

    return p







        




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

def set_bit_pattern(self, x):  
    if(type(x) == str):
        if(x.count("1" ) + x.count("0") == len(x)):
            if(len(x) < self.N):
                self.value = int(x, 2)
            else:
               raise ValueError("Bit pattern length exceeds N")
        else:
            raise ValueError("Invalid bit pattern: must contain only '0' and '1'")
    elif(type(x) == int):
        if(countBits(x) <= self.N):
            self.value = x
        else:
            raise ValueError("Integer value exceeds N bits")
    else:
        raise ValueError("Invalid input type: must be a string or integer")
        


def countBits(x):
    return x.bit_length()

#creates mask of n bits and k trailing zeros
def createMask(n, k):
    return ((1 << n) - 1) << k

def countTrailingZeros(x):
   if x == 0:
       return 0
   return (x & -x).bit_length() - 1

def twoscomp(n, bits):
    n = ((1<< bits) -n) % (1 << bits)
