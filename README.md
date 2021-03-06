# Korean Online Speech Recognition
KOSR provides model implements based on transformer for end-to-end korean speech recognition.
And you can train KsponSpeech dataset was processed by referring to [here].

This project includes the models below.
#### Update
* Transformer Joint CTC (testing)
* [Transformer Transducer] (not tested)
* Transformer

## Preparation
You can download dataset at [AI-Hub]. And the structure of the directory should be prepared for getting started as shown below. Preprocesses were used [ESPnet] for normalizing text  from KsponSpeech recipe. It is provided simply as .trn extention files.
```
root
└─ KsponSpeech_01
└─ KsponSpeech_02
└─ KsponSpeech_03
└─ KsponSpeech_04
└─ KsponSpeech_05
└─ KsponSpeech_eval
└─ scripts
```

## Environment
For training transformer and joint CTC, it requires belows.
python>=3.6 & pytorch >= 1.7.0 & torchaudio >= 0.7.0

```
pip install torch==1.7.0+cu101 torchaudio==0.7.0 -f https://download.pytorch.org/whl/torch_stable.html
```

If you want to train transformer-transducer, follow the directions below.
Warp-transducer needs to install gcc++5 and export CUDA environment variable. It's not tested yet.

CUDA_HOME settings

```
export CUDA_HOME=$HOME/tools/cuda-9.0 # change to your path
export CUDA_TOOLKIT_ROOT_DIR=$CUDA_HOME
export LD_LIBRARY_PATH="$CUDA_HOME/extras/CUPTI/lib64:$LD_LIBRARY_PATH"
export LIBRARY_PATH=$CUDA_HOME/lib64:$LIBRARY_PATH
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH
export CFLAGS="-I$CUDA_HOME/include $CFLAGS"
```

Install gcc++5 and update alternatives

```
sudo add-apt-repository ppa:ubuntu-toolchain-r/test
sudo apt-get update
sudo apt-get install gcc-5 g++-5
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-5 1
```

## Usage
Before training, you should already get Ai-Hub dataset. And you needs to check configuration in conf directory and set batch size as fittable as your gpu environment. If you want to use custom configuration, use conf option(default: config/ksponspeech_transducer_base.yaml).
```
python train.py [--conf config-path]
```
Checkpoint directory will be created automatically after training. You can check saved model at checkpoint directory.
If you want to train continuosly, use continue_from option.
```
python train.py --conf model-configuration --load_model saved-model-path
```

Transformer-ls
```
python train.py --conf conf/ksponspeech_transformer_base.yaml
```

Transformer jointed CTC
```
python train.py --conf conf/ksponspeech_transformer_joint_ctc_base.yaml
```

## Results
Paper used 3-grams language model. You can build N-grams using KenLM.

|Data|Model|CER|WER|Preprocessing|
|----|------|---|---|-------------|
|Eval-Clean|Transformer (β=6)|14%|32%|Filter Bank + SpecAugment|

[Transformer Transducer]:https://arxiv.org/pdf/2002.02562.pdf
[here]:https://www.mdpi.com/2076-3417/10/19/6936
[AI-Hub]: https://www.aihub.or.kr/aidata/105
[ESPnet]: https://github.com/espnet/espnet/tree/master/egs/ksponspeech/asr1

## Author
Email: 406023@naver.com
