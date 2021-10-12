# 数据配置项

## dataset 相关配置
import string

train_data_path = "/Users/sjhuang/Documents/docs/dataset/captcha/train_data"
test_data_path = "/Users/sjhuang/Documents/docs/dataset/captcha/test"
train_rate = 0.9
# resize 大小
channel = 3
height = 32
width = 100
batch_size = 64


## cnn_rnn_ctc model params
crc_train_config = {
   "lr": 1e-3,
   "m_lr": 1e-4,
   "momentum": 0.9,
   "epochs":  1000,
   "early_stop": 200,
   "map_to_seq_hidden": 64,
   "rnn_hidden": 256,
   "leaky_relu": False,
   "checkpoints_dir":"checkpoints/crc_checkpoints/",
   "reload_checkpoint": "checkpoints/crc_checkpoints/crc.pt",
   "show_interval": 1,
   'valid_interval': 5,
   "drop_last":True,
   "num_workers":3,
   "decode_method":"beam_search",
   "beam_size":10,
   "name":"crc"
}


## labels and chars only 英文和数字
CHARS = "-"+string.digits + string.ascii_lowercase
CHAR2LABEL = {char: i for i, char in enumerate(CHARS)}
LABEL2CHAR = {label: char for char, label in CHAR2LABEL.items()}
num_class = len(LABEL2CHAR)