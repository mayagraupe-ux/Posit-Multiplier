module fsm_tb ;

reg clk;
reg in;
reg reset;
reg done;
reg [3: 0] count;

LOD_fsm uut (.clk( clk), .in(in), .reset(reset), .done(done), .count(count));

  // Clock generation: 10 ns period
    initial clk = 0;
    always #5 clk = ~clk;

initial begin

clk =0;
reset =0;
in =0;

  $monitor("Time=%0dns | Reset=%b | In=%b | Done=%b | Count=%d", 
                 $time, reset, in, done, count);

//reset
#20;
reset = 1;
#10;
reset = 0;

/*
//scenario 1 : 0001. wait clock cycle between each
in = 1'b0;

#10;

in = 1'b0;
#10;

in = 1'b0;
#10;

in = 1'b0;
#10;

in = 1'b1;
#10;

//extra inputs to make sure fsm actually stopped
in = 1'b0;
#10;
in = 1'b1; 
#10;

*/
//scenario 2: immediate 1
in = 1'b1;
#10;

in = 1'b0;

#10;

 $display(" Final zero count tracked: %d", count);
        $stop;

end



endmodule
