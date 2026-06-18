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
   
   wire		  temp_zero1 = ~(| a[N-1:0]);
   wire		  temp_zero2 = ~( | b[N-1:0]);
   assign zero = temp_zero1 | temp_zero2; 
   
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
   
   
   extraction ext1 (.in(x1), .rc(rc1), .regime(r1), .exp(e1), .mant(m1));
   extraction ext2 (.in(x2), .rc(rc2), .regime(r2), .exp(e2), .mant(m2));
   
   
    

 //multiplication

   //xor the signs
   wire mult_sign = s1^ s2;
   
localparam MW = N - es -1; //max mantissa width

//extract only useful mantissa bits
wire [MW -1: 0] true_m1 = m1[N-1 : N-MW];
wire [MW - 1:0] true_m2 = m2[N-1 : N- MW];

//mulitply mantissas
wire [(2*MW)-1 : 0] mult_mant = true_m1 * true_m2;

//check for over flow
wire mantOver = mult_mant[(2*MW) -1];

//if no overflow, shift everything left by 1 ( we want a leading 1)
wire[(2*MW) -1 : 0] mult_mant_fixed = mantOver ? mult_mant : (mult_mant << 1);

/*
   //multiply mantissa
   wire 	[2*(N-es) +1:0] mult_mant = m1 * m2;
   wire			mantOver = mult_mant[2*(N-es)+1];
   //if there is overflow, we need to shift everything over
   wire		[2 * (N-es) +1: 0]	mult_mant_fixed  = mantOver ? mult_mant : mult_mant << 1;
   
   */

   //add expoinents


   wire		[rs:0]	RG1 = rc1 ? r1 -  1: -r1;
   wire		[rs:0]	RG2 = rc2 ? r2 - 1 : -r2;
wire signed [rs+es:0] scale1 = ($signed(RG1) <<< es) + $signed({1'b0 , e1});
wire signed [rs+es:0] scale2 = ($signed(RG2) <<< es) + $signed({1'b0, e2});

// sum them up with mantissa overflow
wire signed [rs+es+1:0] total_scale = $signed(scale1) + $signed(scale2) + $signed({1'b0, mantOver});

// sparate into Rout and Eout based on sign
wire total_sign = total_scale[rs+es+1];


//for Eout, we just want the remainder
 wire [es-1 :0] Eout = total_scale[es-1:0];
wire signed [rs:0] signed_Rout = (total_scale - $signed({1'b0, Eout})) >>> es;
wire [rs: 0] Rout = total_sign ? -signed_Rout : signed_Rout;

// Absolute value of total scale for easier decoding
//wire [rs+es+1:0] abs_scale = total_sign ? -total_scale : total_scale;

//wire has_remainder = |abs_scale[es-1:0]; // Checks if any exponent bits are 1

//assign Eout = total_sign ? (has_remainder ? -abs_scale[es-1:0] : {es{1'b0}}) 
//                         : abs_scale[es-1:0];

//assign Rout = total_sign ? (abs_scale[rs+es:es] + (has_remainder ? 1 : 0)) 
     //                    : abs_scale[rs+es:es];


/*
   //concatenate together the regime (RG) and E (2^2^es)^k *2^e (and account for if there is overflow)
   wire		[es + rs +1: 0]	eff_exp  = {RG1, e1} + {RG2, e2} +mantOver;
   //take abs value of it
   wire [es +rs: 0]	eff_exp_neg =  eff_exp[es+rs+1] ? -eff_exp : eff_exp;
   //to find e out, you have to see if exp is negative with a remainder or positive to handle it differently when youre reencoding
   wire [es-1:0]	Eout = (eff_exp[es +rs +1] &( |eff_exp_neg[es-1:0])) ? eff_exp[es-1:0] : eff_exp_neg[es-1:0];
 //to find regime out, if pos add 1, if neg with  a remainder also add 1, if neg with no remainder don't add 1
   wire [rs:0]	Rout	= !(eff_exp[es+rs+1]) | (eff_exp[es+rs+1] & eff_exp_neg[es-1:0]) ? eff_exp_neg[es+rs:es] +1 : eff_exp_neg[es+rs:es];
   
   */

//posit construction
  // localparam		MW = N-es -2;
   //find regime sequence, then exponent, then mantissa, then guard, round and sticky bits
wire regime_bit = total_sign ? 1'b0 : 1'b1;
wire term_bit = total_sign ? 1'b1 : 1'b0;

wire signed [2 * N-1 + 3: 0] rem;
   assign rem = {{N{regime_bit}},
 term_bit,
 Eout, 
 mult_mant_fixed[(2*MW) -2: MW-1], //main fraction bits
 mult_mant_fixed[MW-1], //guard bit
|(mult_mant_fixed[MW-2:0])}; //sticky bit


wire signed [2 * N + es + MW: 0] rem_shift;
assign rem_shift = rem >> (N- Rout - 2);		

     
   //rounding - round to nearest even
   //ulp_add = G.(R+S) + L.G.(!(R+S))
  wire L=rem_shift[N+4], G = rem_shift[N+3], R = rem_shift[N+2], S=|rem_shift[N+1:0];	 
wire ulp_add;    
   assign ulp_add =(Rout < N-es -2) ? (( G & (R +S) ) | (L & G & (!( R | S )))) : 0;
wire [2 * N-1 +3: 0] rem_rounded;
wire [2 *N-1 +3: 0] temp = {{(2*N+3){1'b0}}, ulp_add};
   assign  rem_rounded = (rem_shift + temp);
wire [2 * N-1+3 : 0] rem_signed;
   
//assign rem_signed = (mult_sign == 0) ? rem_rounded : -rem_rounded;
	wire [N-1: 0] pos_posit;
assign pos_posit = rem_rounded[2*N+1: N+2];
//if should be negative, take 2's comp
assign ans = (zero == 1) ? {N{1'b0}}:
	     (inf) ? {1'b1, {N-1{1'b0}}} :
	     (mult_sign) ? -pos_posit:
				pos_posit;		    

   //final processing
  // assign ans = (!zero | inf ) ? {inf, {(N-1){1'b0}}} : {mult_sign, rem_signed};
   
always @(*) begin
      // Small delay ensures all combinational logic has settled before printing
      #1; 
      $display("--- TIME: %0t ---", $time);
      $display("Inputs:  a = %b, b = %b", a, b);
      $display("Flags:   zero = %b, inf = %b, mult_sign = %b", zero, inf, mult_sign);
      $display("Extracted x1: rc=%b, regime=%d, exp=%b, mant=%b", rc1, r1, e1, m1);
      $display("Extracted x2: rc=%b, regime=%d, exp=%b, mant=%b", rc2, r2, e2, m2);
      $display("Mantissa Mul: mult_mant = %b, mantOver = %b", mult_mant, mantOver);
      $display("Exponent Add: total_scale  = %d, Rout = %d, Eout = %d", total_scale, Rout, Eout);
      $display("Posit Build:  rem = %b", rem);
      $display("Posit Shift:  rem_shift = %b", rem_shift);
      $display("Posit Round:  rem_rounded = %b", rem_rounded);
      $display("Final Output: ans = %b", ans);
      $display("---------------------");
   end
   
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
   wire [N -1: 0] rc_xin = rc ? ~xin : xin;

   wire [bs -1: 0] regime; //k value
   wire		   k_temp;
   wire		   valid;
   
   
   //find k with leading one detector 
   LOD #(.N(N), .bs(bs))  lod (.count(regime), .xin(rc_xin[N-2:0]));


   
 
   
//shift xin over to get rid of the regime  by regime+1 but make sure we don't overshift
   wire[bs:0] total_shift = (regime == N-1) ? (N-1) : (regime +1);
   
   wire [N-2:0]	shifted = xin << total_shift;
   

//get exp values and then flush out exp bits
   assign exp = shifted[N-2: N-2-es+1];
   
//get fraction values  which are remaining bits  
wire [N-1: 0] fraction = shifted << es;
   assign mant = {1'b1, fraction[N-2 :0]};

endmodule // extraction

	 



  module LOD (count,  xin);
 parameter  N= 8;
 parameter  bs = $clog2(N);
   
   input [N-2 : 0] xin;
   output reg [bs:0] count;
 // output	  valid;

   integer	  i;


  always @(*) begin
     count =N; //default if it never finds one
 
     for(i = 0; i<N-1; i=i+1) begin
	if(xin[i] ) begin
	   count =(N-2) -i ;
	  
	   
	end
	
	end
     end

  endmodule // LOD
	    
