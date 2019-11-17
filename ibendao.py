#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
Still being testing...
'''

import os, sys, warnings, datetime, time, subprocess, traceback

########################################################
# In the following block, change basic settings of the experiment
#######################################################
## extra environment variables
EXTRA_EV = {}
for k,v in EXTRA_EV.items():
    os.environ.setdefault(k, v)

## basic settings
CUDA_VISIBLE_DEVICES = '0,1'
TASK_NAME = 'iwslt14-de2en'
MODEL_VAR = 'baseline'
FAIRSEQ_NAME = 'fairseq'
DECODE_LAST_ENSEMBLE = -1
SEND_MAIL = False
SEND_MAIL_TO = 'wyzypa@gmail.com'

## training settings
TRAIN_SETTINGS = {
    '--arch': 'transformer',
    '--share-all-embeddings': True,
    '--lr': 3e-4,
    '--weight-decay': 0.001,
    '--max-tokens': 4096,
    '--update-freq': 1,
    '--max-epoch': 20,
    # '--max-update': '100000',
    '--fp16': True
}
SOLID_TRAIN_SETTINGS = {
    '--ddp-backend=no_c10d': True,
    '--optimizer': 'adam',
    '--adam-betas': '\'(0.9, 0.98)\'',
    '--dropout': 0.3,
    '--clip-norm': 0.0,
    '--lr-scheduler': 'inverse_sqrt',
    '--warmup-init-lr': 1e-7,
    '--warmup-updates': 4000,
    '--min-lr': 1e-9,
    '--criterion': 'label_smoothed_cross_entropy',
    '--label-smoothing': 0.1,
    '--no-progress-bar': True,
    '--log-interval': 1000,
    '--keep-last-epochs': 10,
    '--seed': 0
}

GENERATE_SETTINGS = {
    '--task': 'translation',
    '--batch-size': 32,
    '--beam': 5,
    '--lenpen': 1.0,
    '--remove-bpe': True
}
################# end of configuration block #################

import logging
from logging import Formatter, StreamHandler, FileHandler

if not os.path.isdir('logs'):
    os.system('mkdir logs')

logger = logging.getLogger()
formatter = Formatter(fmt="[%(asctime)s] %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
file_handler = FileHandler('logs/ibendao.log.{}'.format(datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
stream_handler = StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    import torch
except ImportError as e:
    sys.stderr.write('Cannot find torch in environment. Are you in a docker container?\n')
    sys.exit(1)
else:
    if not torch.cuda.is_available():
        warnings.warn('Looks like your environment does not support calculation on GPU...')
        flag = input('Are you sure to resume the script? (y/n)')
        if flag != 'y':
            sys.exit(1)

if not os.path.isdir(os.path.join(BASE_DIR, FAIRSEQ_NAME)):
    sys.stderr.write('Cannot find [{}] at current directory.'.format(FAIRSEQ_NAME))
    sys.exit(1)

start_of_main = time.time()

def concat_cmd(root, **kwargs):
    params = []
    for k,v in kwargs.items():
        if v is True:
            params.append(k)
        else:
            params.append('{} {}'.format(k, v))
    cmd = '{} {}'.format(root.strip(), ' '.join(params))
    return cmd

def send_mail():
    import smtplib
    from email.mime.text import MIMEText

    p = subprocess.Popen('hostname', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if err:
        logger.error('Error During Getting Hostname: {}'.format(err))
        host_name = 'Unknown'
    else:
        host_name = str(out.strip(), encoding='utf-8')

    period = time.time() - start_of_main

    text_msg = 'Your training process based on [{}] for task [{}] in container [{}] has finished.\n' \
               '{:.4f} seconds are consumed.' \
               'Please login and check for the results.'.format(MODEL_VAR, TASK_NAME, host_name, period)

    msg = MIMEText(text_msg, 'plain', 'utf-8')
    msg['Subject'] = 'Training Finished @ {}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    msg['From'] = 'publictakanashi@gmail.com'
    msg['To'] = SEND_MAIL_TO
    try:
        smtp = smtplib.SMTP()
        smtp.connect('smtp.gmail.com', 25)
        smtp.starttls()
        smtp.login('publictakanashi@gmail.com', 'Public@123')
        smtp.sendmail('publictakanashi@gmail.com', SEND_MAIL_TO, msg.as_string())
        smtp.close()
    except Exception as e:
        logger.error('Failed to send email:\n{}'.format(traceback.format_exc(e)))

def main():
    steps = []
    try:
        step = sys.argv[1]
    except IndexError as e:
        steps = ['train', 'generate']
    else:
        steps.append(step)

    input('You will train a [{}] for task [{}] with GPU [{}]. The fairseq components are [{}]. '
              'Press Enter to continue...'.format(MODEL_VAR, TASK_NAME, CUDA_VISIBLE_DEVICES, FAIRSEQ_NAME))

    # os.system('export CUDA_VISIBLE_DEVICES="{}"'.format(CUDA_VISIBLE_DEVICES))
    os.environ.setdefault('CUDA_VISIBLE_DEVICES', CUDA_VISIBLE_DEVICES)

    model_output_dir = os.path.join(BASE_DIR, TASK_NAME, MODEL_VAR, 'model')
    log_output_dir = os.path.join(BASE_DIR, TASK_NAME, MODEL_VAR, 'logs')
    for d in (model_output_dir, log_output_dir):
        if not os.path.isdir(d):
            os.system('mkdir -p \'{}\''.format(d))

    data_bin_dir = os.path.join(BASE_DIR, 'data-bin') if 'data-bin' in os.listdir(BASE_DIR) else \
        os.path.join(BASE_DIR, TASK_NAME, MODEL_VAR, 'data-bin')
    warnings.warn('Using data-bin @ [{}]'.format(data_bin_dir))

    if 'train' in steps:
        # prepare for training
        train_cmd = 'python -u {}/train.py {}'.format(FAIRSEQ_NAME, data_bin_dir)
        TRAIN_SETTINGS.update(SOLID_TRAIN_SETTINGS)
        TRAIN_SETTINGS['--save-dir'] = model_output_dir
        train_cmd = concat_cmd(train_cmd, **TRAIN_SETTINGS)
        train_log_fn = os.path.join(log_output_dir, 'train.log.{}'.format(datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
        train_cmd = '{} 2>&1 | tee {}'.format(train_cmd, train_log_fn)
        logger.info(train_cmd)

        # start training
        train_start_at = time.time()
        rtn_code = os.system(train_cmd)
        train_end_at = time.time()
        train_period = train_end_at - train_start_at
        if rtn_code == 0:
            logger.info('Training is done in [{:.4f}] seconds'.format(train_period))
        else:
            logger.error('Training stopped for error.')
            sys.exit(1)

    if 'generate' in steps:
        if DECODE_LAST_ENSEMBLE == -1:    # use checkpoint_best.pt as trained model
            model = os.path.join(model_output_dir, 'checkpoint_best.pt')
        else:
            logger.info('Generating last {} ensembles'.format(DECODE_LAST_ENSEMBLE))
            model = os.path.join(model_output_dir, 'checkpoint.ensemble{}.pt'.format(DECODE_LAST_ENSEMBLE))
            ensemble_cmd = 'python -u {}/scripts/average_checkpoints.py --inputs {} --output {} --num-epoch-checkpoints {}'\
                .format(FAIRSEQ_NAME, model_output_dir, model, DECODE_LAST_ENSEMBLE)
            rtn_code = os.system(ensemble_cmd)
            if rtn_code != 0:
                logger.info('Failed to ensemble.')
                sys.exit(1)

        # prepare for generating
        generate_cmd = 'python -u {}/generate.py {}'.format(FAIRSEQ_NAME, data_bin_dir)
        GENERATE_SETTINGS['--path'] = model
        generate_cmd = concat_cmd(generate_cmd, **GENERATE_SETTINGS)
        gen_log_fn = os.path.join(log_output_dir, 'generate.log.{}'.format(datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
        generate_cmd = '{} 2>&1 | tee {}'.format(generate_cmd, gen_log_fn)
        logger.info(generate_cmd)

        # start generating
        gen_start_at = time.time()
        rtn_code = os.system(generate_cmd)
        gen_end_at = time.time()
        gen_period = gen_end_at - gen_start_at
        if rtn_code == 0:
            logger.info('Generating is done in [{:.4f}] seconds'.format(gen_period))
        else:
            logger.error('Generation stopped for error.')
            sys.exit(1)

        os.system('tail -n 1 {} >> {}'.format(gen_log_fn, train_log_fn))

    if 'train' in steps and SEND_MAIL:    # a simple generation will not trigger mail sending.
        time_to_send_mail = time.time()
        if time_to_send_mail - start_of_main < 60:
            # if the whole process ends within one minute, there probably are some errors.
            warnings.warn('I think the process ends too fast. So I won\'t send mail.')
        else:
            send_mail()

if __name__ == '__main__':
    main()
