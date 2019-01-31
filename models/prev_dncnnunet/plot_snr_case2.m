% plot snr_case2

clear all;
close all;
caxis = [-3 7];

%% load maxV
% maxV = load('maxV.mat');
% maxV = maxV.maxV;
maxV = 25.0;

%% noisy input

load('../../prepare_data/spie2d_customize/test_snr_case2/1e+07/test1.mat');

img_noisy = currentImage;
figure,imagesc(log10(img_noisy),caxis);
cb = colorbar('northoutside');
xlabel('mm');
ylabel('1e7');

%% clean 

load('../../prepare_data/spie2d_customize/test_snr_case2/1e+08/test1.mat');

img_noisy = currentImage;
figure,imagesc(log10(img_noisy),caxis);
cb = colorbar('northoutside');
xlabel('mm');
ylabel('1e8');

%% model
load('./test_snr_case2.mat');  % 3d array: sample x 2d images
currentimg = output_clean(1,:,:);

% undo normalization, revert log(x + 1) = y  => x = exp(y) - 1
currentimg = squeeze(currentimg) * maxV;
x = exp(currentimg) - 1;

max(max(x))
min(min(x))

pos = x < 0.0;
x(pos) = 1e-8;

figure,imagesc(log10(x),caxis);
cb = colorbar('northoutside');
xlabel('mm')
ylabel('1e7-NN')
