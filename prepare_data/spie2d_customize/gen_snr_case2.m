clear all; close all; clc;

mcxseed=111;

N=100; % repeat N times with different rand seeds

%% set up the output dir

% Top-level Dir
% topFolderName='./test_snr_case2';
% if ~exist(topFolderName, 'dir')  mkdir(topFolderName); end

testDir='./test_snr_case2';
if ~exist(testDir, 'dir')  mkdir(testDir); end

% testDir = sprintf('%s/het_default_square_x10', topFolderName);
% if ~exist(testDir, 'dir')  mkdir(testDir); end

testDir_p7 = sprintf('%s/%1.0e', testDir, 1e7);
if ~exist(testDir_p7, 'dir')  mkdir(testDir_p7); end

testDir_p8 = sprintf('%s/%1.0e', testDir, 1e8);
if ~exist(testDir_p8, 'dir')  mkdir(testDir_p8); end


%% generate N randseeds

rand_seed = randi([1 2^31-1], 1, N);
if (length(unique(rand_seed)) < length(rand_seed)) ~= 0
    error('There are repeated random seeds!')
end


%% read the image

% the test image is grayscle, text is black, bg is white
% size is 100 x 100
%input_img = imread('./images/square.png');  % 
%img_modify = uint8(input_img < 255); % make the text 1, others bg is 0 255

%img_modify = uint8(ones(100,100)); % raise 1 to distinguish from the background
% imagesc(img_modify)

img_modify = ones(100,100);
img_modify(31:70,11:50) = 2; %  40x40, located at 10 along x-axis


%%

for sid = 1:N
mcxseed = rand_seed(sid);

% figure;

% 1e7
[cwdata, ~, ~] = rand_2d_mcx_grid_test2(1e7, img_modify, 123, mcxseed);
currentImage = cwdata;
fname = sprintf('%s/test%d.mat', testDir_p7,  sid);
fprintf('Generating %s\n',fname);
feval('save', fname, 'currentImage');

% subplot(121);
% imagesc(log10(abs(cwdata)));

% 1e8
[cwdata, ~, ~] = rand_2d_mcx_grid_test2(1e8, img_modify, 123, mcxseed);
currentImage = cwdata;
fname = sprintf('%s/test%d.mat', testDir_p8,  sid);
fprintf('Generating %s\n',fname);
feval('save', fname, 'currentImage');

% subplot(122);
% imagesc(log10(abs(cwdata)));
% break

end
