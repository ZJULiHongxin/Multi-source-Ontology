%使用GPU
parallel.gpu.GPUDeviceManager.instance.selectDevice(1);
classNames = ["Hand" "Background"];
labels = [1 2];
% 使用 imageDatastore 和 pixelLabelDatastore 加载训练数据
imageFolderTrain = 'D:\ImageNet\hand_labels\HandSegmentation\Experiment\SquareTraining';
labelFolderTrain = 'D:\ImageNet\hand_labels\HandSegmentation\Experiment\SquareLabels';
imageTrain = imageDatastore(imageFolderTrain);
labelTrain= pixelLabelDatastore(labelFolderTrain,classNames,labels);

% 观察带标签的图片样例
% I = read(imds);
% C = read(pxds);
% categories(C{1})
% B = labeloverlay(I,C{1});
% figure
% imshow(B)

% 数据增强
augmenter = imageDataAugmenter('RandXReflection',true,...
    'RandXTranslation',[-10 10],'RandYTranslation',[-10 10]);

pximdsTrain = pixelLabelImageDatastore(imageTrain,labelTrain, ...
    'DataAugmentation',augmenter);

% 加载验证数据
imageFolderValid='D:\ImageNet\hand_labels\HandSegmentation\Experiment\Valid';
labelFolderTrain='D:\ImageNet\hand_labels\HandSegmentation\Experiment\ValidLabels';
Validset=imageDatastore(imageFolderValid);
Validlabels=pixelLabelDatastore(labelFolderTrain,classNames,labels);
validdata = pixelLabelImageDatastore(Validset,Validlabels);

% 创建一个用于训练数据的数据源，并获取每个标签的像素计数。
tbl = countEachLabel(pximdsTrain)

% 使用逆频率加权计算类权重
numberPixels = sum(tbl.PixelCount);
frequency = tbl.PixelCount / numberPixels;
classWeights = 1 ./ frequency;

% 创建一个用于像素分类的网络，它具有一个图像输入层，输入大小对应于输入图像的大小。接下来，指定对应于卷积层、批量归一化层和 ReLU 层的三个块。对于每个卷积层，指定 32 个具有递增扩张系数的 3×3 过滤器，并通过将 'Padding' 选项设置为 'same' 来指定将输入填充为与输出相同的大小。要对像素进行分类，请包括一个具有 K 个 1×1 卷积的卷积层（其中 K 是类的数量），其后是一个 softmax 层和一个具有逆类权重的 pixelClassificationLayer。
inputSize = [720 720 3];
filterSize = 6;
numFilters = 32;
numClasses = numel(classNames);

disp('Building network...')
layers = [
    imageInputLayer(inputSize,'Name','input')
    
    convolution2dLayer(filterSize,numFilters,'DilationFactor',1,'Padding','same','Name','conv1')
    batchNormalizationLayer('Name','BN1')
    reluLayer('Name','ReLU1')
    
    convolution2dLayer(filterSize,numFilters,'DilationFactor',2,'Padding','same','Name','conv2')
    batchNormalizationLayer('Name','BN2')
    reluLayer('Name','ReLU2')
    
    convolution2dLayer(filterSize,numFilters,'DilationFactor',4,'Padding','same','Name','conv3')
    batchNormalizationLayer('Name','BN3')
    reluLayer('Name','ReLU3')
    
    convolution2dLayer(1,numClasses,'Name','conv4')
    softmaxLayer('Name','softmax')
    pixelClassificationLayer('Classes',classNames,'ClassWeights',classWeights,'Name','output')];

% lgraph = layerGraph(layers);
% analyzeNetwork(lgraph);

checkpointPath='D:\ImageNet\hand_labels\HandSegmentation\Experiment';

options = trainingOptions('sgdm', ...
    'Momentum', 0.9, ...
    'MaxEpochs', 2, ...
    'MiniBatchSize', 20, ... 
    'ValidationData',validdata, ...
    'ValidationFrequency',40, ...
    'InitialLearnRate', 1e-2, ...
    'LearnRateSchedule','piecewise',...
    'LearnRateDropFactor',0.5,...
    'LearnRateDropPeriod',40, ...
    'L2Regularization',0.01, ...
    'Shuffle','every-epoch', ...
    'Plots','training-progress',...
    'ExecutionEnvironment','cpu', ...
    'CheckpointPath',checkpointPath,...
    'verbose',true,...
    'VerboseFrequency',10);
disp('Start training...')
net = trainNetwork(pximdsTrain,layers,options);