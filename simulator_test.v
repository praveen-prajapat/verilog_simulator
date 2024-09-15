module Simulator_test(
    input wire a,
    input wire b,
    input wire c,
    input wire d,
    input wire e,
    output wire x
);
    wire j, k, l;

    and a0 (j, a, b);  
    and a1 (k, c, d);  
    or  o0 (l, j, k);  
    and a3 (x, l, e);  

endmodule