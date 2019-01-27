clc;
clear all;

addpath('../mcx')
addpath('../mcx/mcxlab')


%%
% the prop_num from 2 to 21 (20)
% for each object, 1 to 100 random seed (100)
% 1e5 and 1e8 photons

% Top-level Dir
topFolderName='../../data/rand2d/test';
if ~exist('../../data/rand2d/test', 'dir')  mkdir(topFolderName); end

% ../../data/rand2d/1e5
dir_phn_noisy = sprintf('%s/%1.0e', topFolderName, 1e5);
if ~exist(dir_phn_noisy, 'dir')  mkdir(dir_phn_noisy); end
   
% ../../data/rand2d/1e8
dir_phn_clean = sprintf('%s/%1.0e', topFolderName, 1e8);
if ~exist(dir_phn_clean, 'dir')  mkdir(dir_phn_clean); end



N = 10;


% Generate new random seed for Monte Carlo simulation
rand_seed = randi([1 2^31-1], 1, N);
if (length(unique(rand_seed)) < length(rand_seed)) ~= 0
error('There are repeated random seeds!')
end


testID = 1;

for i = 1:10
   for j = 1 : N 
    rand_sd = rand_seed(j);
    
    % noisy
    [currentImage, ~, ~] = rand_2d_mcx(1e5, i, [100 100], rand_sd);
    
    fname = sprintf('%s/test%d.mat', dir_phn_noisy,  testID);
    fprintf('Generating %s\n',fname);
    feval('save', fname, 'currentImage');
    
    % clean
    [currentImage, ~, ~] = rand_2d_mcx(1e8, i, [100 100], rand_sd);
    
    fname = sprintf('%s/test%d.mat', dir_phn_clean,  testID);
    fprintf('Generating %s\n',fname);
    feval('save', fname, 'currentImage');
    
    testID = testID + 1;
    %break
   end
   %break
end

