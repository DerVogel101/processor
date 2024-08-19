ldi b 0b0001_0000
ldi c 0b0001_1000
add a b c
out a o0
: loop
nop
jmp loop