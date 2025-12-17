function colorSeq = EncodeSOLID( seq )

k = {'AT','CT','GT','TT',...
    'AG', 'CG', 'GG', 'TG',...
    'AC', 'CC', 'GC', 'TC',...
    'AA', 'CA', 'GA', 'TA'};
v = {2,4,1,3,4,2,3,1,1,3,2,4,3,1,4,2};
coding = containers.Map(k,v);
colorSeq = [coding(seq(1:2))];
for i=3:numel(seq)
    s = seq((i-1):i);
    colorSeq = [colorSeq coding(s)];
end
end

