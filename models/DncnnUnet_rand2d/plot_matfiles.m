clear all;
close all;


caxis = [-3 7];

% load maxV

maxV = load('maxV.mat');
maxV = maxV.maxV;
%%
prefix = '../../data/rand2d/1e+07/test';
for tid = 1:100
    filename = [prefix num2str(tid) '.mat'];
    fprintf('filename = %s\n',filename);
    load(filename);
    
    img_noisy = currentImage;
    figure,imagesc(log10(img_noisy),caxis);
    cb = colorbar('northoutside');
    xlabel('mm')
    ylabel('1e7')
end
