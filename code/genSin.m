A = zeros(313, 2);
for i = 1:length(A)
    x = rand()*6.28;
    A(i,1) = x;
    A(i,2) = sin(x);
end
    