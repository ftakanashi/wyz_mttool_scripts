#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
A script that can automatically run train and generate (or respectively) commands based on fairseq components.
The script should be placed in the directory where fairseq components are put.
You may change the parameters/settings in the following CONFIGURATION BLOCK to change the behavior of the script.
v0.0.1
'''

import os, sys, warnings, datetime, time, subprocess, traceback

#######################################################################
###                                                                 ###
### In the following block, change basic settings of the experiment ###
###                                                                 ###
#######################################################################

## extra environment variables
# set extra environment in the dictionary as key-value pairs if your program need them.
EXTRA_EV = {}
for k,v in EXTRA_EV.items():
    os.environ.setdefault(k, v)

## basic settings
CUDA_VISIBLE_DEVICES = '0,1'
TASK_NAME = 'iwslt14-de2en'    # logs and checkpoints are saved at ./$TASK_NAME/$MODEL_VAR
MODEL_VAR = 'baseline'
FAIRSEQ_NAME = 'fairseq'    # decide which fairseq component to use to do all the work
DECODE_LAST_ENSEMBLE = -1
SEND_MAIL = False    # determine whether to send an e-mail when training (and generating) finish.
SEND_MAIL_TO = 'wyzypa@gmail.com'
HOST_NAME = 'NOT_SET' # set the hostname of the current machine, which helps to identify the task.

## training settings
TRAIN_SETTINGS = {
    # following training parameters are often changed for ablation study, so I put them at the top.
    '--source-lang': 'de',
    '--target-lang': 'en',
    '--arch': 'transformer',
    '--share-all-embeddings': True,
    '--lr': 3e-4,
    '--weight-decay': 0.001,
    '--max-tokens': 4096,
    '--update-freq': 1,
    '--max-epoch': 20,    # todo change to max-updates if necessary
    '--fp16': True
}
SOLID_TRAIN_SETTINGS = {
    # following training parameters usually don't change much, but you can modify them if necessary
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
    # '--keep-last-epochs': 10    # uncomment this option if needed
}

## generation settings
GENERATE_SETTINGS = {
    '--source-lang': 'de',
    '--target-lang': 'en',
    '--task': 'translation',
    '--batch-size': 32,
    '--beam': 5,
    '--lenpen': 1.0,
    '--remove-bpe': True
}
##################################
### end of configuration block ###
##################################

import logging
from logging import Formatter, StreamHandler, FileHandler

if not os.path.isdir('logs'):
    os.system('mkdir logs')

logger = logging.getLogger()
formatter = Formatter(fmt="[%(asctime)s] %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
# file_handler = FileHandler('logs/ibendao.log.{}'.format(datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
file_handler = FileHandler('logs/ibendao.log.{}.{}.{}'.
                           format(TASK_NAME, MODEL_VAR, FAIRSEQ_NAME))
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

start_of_main = time.time()

def concat_cmd(root, **kwargs):
    params = []
    for k,v in kwargs.items():
        if type(v) is bool:
            if v:
                params.append(k)
        else:
            params.append('{} {}'.format(k, v))
    cmd = '{} {}'.format(root.strip(), ' '.join(params))
    return cmd

def get_container_id():
    p = subprocess.Popen('hostname', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if err:
        logger.error('Error During Getting Hostname: {}'.format(err))
        cid = 'Unknown'
    else:
        cid = str(out.strip(), encoding='utf-8')

    return cid

def send_mail(final_res=None):
    import smtplib
    from email.mime.text import MIMEText

    period = time.time() - start_of_main

    container_id = get_container_id()

    global HOST_NAME

    text_msg = 'Your training process based on [{}] for task [{}] in [{}:{}] has finished.\n' \
               '{:.4f} seconds are consumed.' \
               'Please login and check for the results.'.format(MODEL_VAR, TASK_NAME, HOST_NAME, container_id, period)

    if final_res:
        text_msg += '\nFinal result is [{}]'.format(str(final_res, encoding='utf-8'))

    msg = MIMEText(text_msg, 'plain', 'utf-8')
    msg['Subject'] = 'Training Finished @ {}:{}'.format(HOST_NAME.upper(), os.path.join(BASE_DIR, TASK_NAME, MODEL_VAR))
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

    try:
        if os.getenv('TZ') is None:
            input('Aware that TimeZone environment variable not set. If you want to get correct local time,'
                  'please set the variable by doing like: [export TZ="Asia/Tokyo"]\n'
                  'Press enter/Ctrl+C to continue/stop...\n')

        global HOST_NAME
        if HOST_NAME == 'NOT_SET':
            _hostname = input('Aware that you did not set the hostname for this task.\n'
                              'It is better to set one (press enter to skip): ')
            if _hostname.strip() != '':
                HOST_NAME = _hostname.strip()

        input('You will train a [{}] for task [{}] with GPU [{}:{}].\nThe fairseq components are [{}].\n'
              'Logs and checkpoints are saved at [{}].\nPress enter/Ctrl+C to continue/stop...\n'
              .format(MODEL_VAR, TASK_NAME, HOST_NAME, CUDA_VISIBLE_DEVICES, FAIRSEQ_NAME,
                      os.path.join(BASE_DIR, TASK_NAME, MODEL_VAR)))
    except KeyboardInterrupt as e:
        logger.error('User stopped process.')
        sys.exit(1)

    if not os.path.isdir(os.path.join(BASE_DIR, FAIRSEQ_NAME)):
        sys.stderr.write('Cannot find [{}] at current directory.\n'.format(FAIRSEQ_NAME))
        sys.exit(1)

    os.environ.setdefault('CUDA_VISIBLE_DEVICES', CUDA_VISIBLE_DEVICES)

    model_output_dir = os.path.join(BASE_DIR, TASK_NAME, MODEL_VAR, 'model')
    log_output_dir = os.path.join(BASE_DIR, TASK_NAME, MODEL_VAR, 'logs')
    for d in (model_output_dir, log_output_dir):
        if not os.path.isdir(d):
            os.system('mkdir -p \'{}\''.format(d))

    the_script = os.path.abspath(__file__)
    os.system('cp {} {}'.format(the_script, os.path.join(BASE_DIR, TASK_NAME, MODEL_VAR)))    # copy the script to target dir

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
        try:
            import fairseq
        except ImportError as e:
            has_fairseq = False
        else:
            has_fairseq = True
        if DECODE_LAST_ENSEMBLE == -1 or not has_fairseq:    # use checkpoint_best.pt as trained model
            model = os.path.join(model_output_dir, 'checkpoint_best.pt')
            if not has_fairseq:
                logger.warning('fairseq not found in your environment, so cannot ensemble checkpoints by script.\n'
                               'To fix the error, please run "pip install fairseq"(which will not change your component specified above.)')
        else:
            logger.info('Generating last {} ensembles'.format(DECODE_LAST_ENSEMBLE))
            model = os.path.join(model_output_dir, 'checkpoint.ensemble{}.pt'.format(DECODE_LAST_ENSEMBLE))
            ensemble_cmd = 'python -u {}/scripts/average_checkpoints.py --inputs {} --output {} --num-epoch-checkpoints {}'\
                .format(FAIRSEQ_NAME, model_output_dir, model, DECODE_LAST_ENSEMBLE)
            logger.info(ensemble_cmd)
            rtn_code = os.system(ensemble_cmd)
            if rtn_code != 0:
                logger.info('Failed to ensemble. Probably you didn\'t install fairseq into python but only used its code?')
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

        if 'train' in steps:
            # only append generate bleu to train log if the train is done
            os.system('tail -n 1 {} >> {}'.format(gen_log_fn, train_log_fn))

    if 'train' in steps and SEND_MAIL:    # a simple generation will not trigger mail sending.
        time_to_send_mail = time.time()
        if time_to_send_mail - start_of_main < 60:
            # if the whole process ends within one minute, there probably are some errors.
            warnings.warn('I think the process ends too fast. So I won\'t send mail.')
        else:
            if 'generate' not in steps:
                final_res_row = 'Generate not in commands so there is no result...'
            else:
                p = subprocess.Popen('tail -n 1 {}'.format(train_log_fn), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = p.communicate()
                final_res_row = 'Final Test Result Unknown' if err else out.strip()
                logger.info(final_res_row)

            send_mail(final_res_row)

if __name__ == '__main__':
    main()
