x = rand(100, 1);
y = zeros(100, 1);

y(1) = x(1);
y(2) = x(2);

A = zeros(98, 4);

for i=3:100
    y(i) = sqrt(x(i)) - 0.5*sin(y(i-1)) + 0.4*y(i-2);
    A(i-2, :) = [x(i) y(i-1) y(i-2) y(i)]
end

plot(x)
hold all
plot(y)