A = zeros(121, 3);

i = 1;
for x = -10:10
    for y = -10:10
        xn = x;
        yn = y;
        if x == 0
            xn = 0.001;
        end
        if y == 0
            yn = 0.001;
        end
        f = (sin(xn)*sin(yn))/(xn*yn);
        A(i, :) = [xn yn f];
        i = i+1;
    end
end