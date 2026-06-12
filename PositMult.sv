module mult( a,  b, inf, zero, ans

	    );

  
   
   parameter N = 8;
   parameter es = 2;
   parameter rs = $clog2(N);
   

   input [N-1:0] a, b;
   output	 inf, zero;

   output [N-1:0] ans;
   
 
//data extraction
   //get signs
   
   wire		  s1 = a[N-1];
   wire		  s2 = b[N-1];
   
   //check for zeros (all zeros)
   
   wire		  temp_zero1 = | a[N-1:0];
   wire		  temp_zero2 = | b[N-1:0];
   assign zero = temp_zero1 & temp_zero2; // one if the value is nonzero, zero  if it is 0 - if either input is 0, it will become 0 and the multiplication is 0
   
   //check for infinity (sign is 1, rest are 0)
   
   wire temp_inf1 = a[N-1] & (~a[N-2:0]);
   wire	temp_inf2 = b[N-1] & (~b[N-2:0]);
   assign inf = temp_inf1 | temp_inf2; // if either one is infinity, flag will be 1
   
   
   //take 2s comp if needed
   wire [N-1: 0]  x1 = s1 ? -a : a;
   wire [N-1 :0]  x2 = s2 ? -b : b;
   //extract
   wire [rs-1:0]  r1, r2;
   wire [es-1:0]  e1, e2;
   wire [N-1:0]	  m1,m2;
   wire		  rc1, rc2;
   
   
   extraction ext1 (.in(a), .rc(rc1), .regime(r1), .exp(e1), .mant(m1));
   extraction ext2 (.in(b), .rc(rc2), .regime(r2), .exp(e2), .mant(m2));
   
   
    

 //multiplication

   //xor the signs
   wire mult_sign = s1^ s2;
   
   //multiply mantissa
   wire 	[2*(N-es) +1:0] mult_mant = m1 * m2;
   wire			mantOver = mult_mant[2*(N-es)+1];
   //if there is overflow, we need to shift everything over
   wire		[2 * (N-es) +1: 0]	mult_mant_fixed  = mantOver ? mult_mant : mult_mant << 1;
   
   

   //add expoinents

   wire		[rs-1:0]	RG1 = rc1 ? r1 -  1: -r1;
   wire		[rs-1:0]	RG2 = rc2 ? r2 - 1 : -r2;
   //concatenate together the regime (RG) and E (2^2^es)^k *2^e (and account for if there is overflow)
   wire		[es + rs +1: 0]	eff_exp  = {RG1, e1} + {RG2, e2} +mantOver;
   //take abs value of it
   wire [es +rs: 0]	eff_exp_neg =  eff_exp[es+rs+1] ? -eff_exp : eff_exp;
   //to find e out, you have to see if exp is negative with a remainder or positive to handle it differently when youre reencoding
   wire [es-1:0]	Eout = (eff_exp[es +rs +1] &( |eff_exp_neg[es-1:0])) ? eff_exp[es-1:0] : eff_exp_neg[es-1:0];
 //to find regime out, if pos add 1, if neg with  a remainder also add 1, if neg with no remainder don't add 1
   wire [rs:0]	Rout	= !(eff_exp[es+rs+1]) | (eff_exp[es+rs+1] & eff_exp_neg[es-1:0]) ? eff_exp_neg[es+rs:es] +1 : eff_exp_neg[es+rs:es];
   
   

//posit construction
   localparam		MW = N-es -2;
   //find regime sequence, then exponent, then mantissa, then guard, round and sticky bits
wire [2 * N-1 +3: 0] rem;
   assign rem = {{N{!eff_exp[es+rs+1]}}, eff_exp[es+rs+1], Eout, 
 mult_mant_fixed[2*MW -1: MW], mult_mant_fixed[MW-1: MW-2], |(mult_mant_fixed[MW-3:0])};
wire [2 * N-1 +3: 0] rem_shift;
assign rem_shift = rem >> Rout;			     
   //rounding - round to nearest even
   //ulp_add = G.(R+S) + L.G.(!(R+S))
  wire L=rem_shift[N+4], G = rem_shift[N+3], R = rem_shift[N+2], S=|rem_shift[N+1:0];	 
wire ulp_add;    
   assign ulp_add =(Rout < N-es -2) ? (( G & (R +S) ) | (L & G & (!( R | S )))) : 0;
wire [2 * N-1 +3] rem_rounded;
wire [2 *N-1 +3: 0] temp;
assign temp = '0;
assign temp[0] = ulp_add;
   assign  rem_rounded = (rem_shift + temp);
wire [2 * N-1+3] rem_signed;
   assign rem_signed = (mult_sign == 0) ? rem_rounded : -rem_rounded;
			    

   //final processing
   assign ans = (zero | inf ) ? {inf, {(N-1){1'b0}}} : {mult_sign, rem_signed};
   
   
endmodule // mult

////////

module extraction (in, rc, regime, exp, mant
);

 
   
   parameter N=8;
   parameter bs = $clog2(N);
   parameter es =2;

   input [N-1: 0]	in;
   output	  rc; //whether regime starts with 0 or 1
   output [bs-1: 0] regime;
   output [es-1: 0] exp;
   output [N-1 :0] mant;

   wire [N-1:0]	      xin = in;

   assign rc = xin[N-2];
   //if rc is 1, we need to flip it all to 0 to get leading one detector
   wire rc_xin = rc ? ~xin : xin;

   wire [bs -1: 0] regime; //k value
   wire		   k_temp;
   wire		   valid;
   
   
   //find k with leading one detector 
   LOD #(.N(N-1), .bs(bs))  lod (.count(regime), .xin(xin));


   
 
   
//shift xin over to get rid of the regime  by regime+1 but make sure we don't overshift
   wire[bs:0] total_shift = (regime == N-1) ? (N-1) : (regime +1);
   
   wire [N-2:0]	shifted = rc_xin << total_shift;
   

//get exp values and then flush out exp bits
   assign exp = shifted[N-2: N-2-es+1];
   
//get fraction values  which are remaining bits  
   assign mant = shifted << es ;

endmodule // extraction

	 



  module LOD (count,  xin);
 parameter  N= 8;
 parameter  bs = $clog2(N);
   
   input [N-1 : 0] xin;
   output logic [bs-1:0] count;
 // output	  valid;

   integer	  i;

  always @(*) begin
     count =0; //default if it never finds one
    
     for(i = N-1; i>=0; i=i-1) begin
	if(xin[i]) begin
	   count =i;
	   break;
	   
	end
	
	end
     end

  endmodule // LOD
	    
