import torch
import torch.nn as nn
from tqdm import tqdm
import os

from kosr.utils.metrics import metrics
from kosr.utils import make_chk, train_log, valid_log, epoch_log, chk_path, logger
from kosr.trainer.checkpoint import save

def train_and_eval(epochs, model, optimizer, criterion, train_dataloader, valid_dataloader, max_norm=5, saved_epoch=None, print_step=100, epoch_save=True):
    best_loss = 10101.0
    bl_epoch = 0
    best_wer = 10101.0
    bw_epoch = 0
    
    logger.info("checkpoint saves in {} directory".format(chk_path))
    os.makedirs(chk_path, exist_ok=True)
    if saved_epoch is not None:
        saved_epoch = saved_epoch + 1
    else:
        saved_epoch = 0
    
    for epoch in range(saved_epoch, epochs):
        train_loss, train_wer = train(model, optimizer, criterion, train_dataloader, epoch, max_norm, print_step)
        valid_loss, valid_wer = valid(model, criterion, valid_dataloader, epoch)
        if best_loss>valid_loss:
            best_loss = valid_loss
            bl_epoch = epoch
            save(os.path.join(chk_path, 'best_loss.pth'), epoch, model, optimizer, train_loss)
            
        if best_wer>valid_wer:
            best_wer = valid_wer
            bw_epoch = epoch
            save(os.path.join(chk_path, 'best_wer.pth'), epoch, model, optimizer, valid_loss)
        
        if epoch_save:
            save(os.path.join(chk_path, f"{epoch}_.pth"), epoch, model, optimizer, valid_loss)
            
        save(os.path.join(chk_path, 'last.pth'), epoch, model, optimizer, valid_loss)
        logger.info(epoch_log.format("info", epoch, bw_epoch, best_wer, bl_epoch, best_loss))
            
            

def train(model, optimizer, criterion, dataloader, epoch, max_norm=400, print_step=100):
    losses = 0.
    cer = 0.
    wer = 0.
    step = 0
    model.train()
    pbar = tqdm(dataloader)
    for batch in pbar:
        optimizer.zero_grad()

        inputs, targets, input_length, target_length = batch
        
        if torch.cuda.is_available():
            inputs = inputs.cuda()
            targets = targets.cuda()

        preds, targets = model(inputs, input_length, targets)

        loss = criterion(preds, targets)
        #loss = criterion(preds.view(-1,preds.size(-1)), targets.view(-1))
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), max_norm=max_norm)
        optimizer.step()
        
        losses += loss.item()
        
        y_hats = preds.max(-1)[1]
        #print(y_hats[0], targets[0])

        _cer, _wer = metrics(y_hats, targets)
        cer += _cer
        wer += _wer
        step += 1
        pbar.set_description(train_log.format('training', epoch, losses/step, cer/step, optimizer._rate))
        #if step%print_step==0:
        #    logger.info(train_log.format('training', epoch, losses/step, cer/step, optimizer._rate))
            
    return losses/step, wer/step
        
def valid(model, criterion, dataloader, epoch, search='greedy'):
    losses = 0.
    cer = 0.
    wer = 0.
    step = 0
    model.eval()
    pbar = tqdm(dataloader)
    with torch.no_grad():
        for batch in pbar:
            inputs, targets, input_length, target_length = batch

            if torch.cuda.is_available():
                inputs = inputs.cuda()
                targets = targets.cuda()
            
            preds, targets, y_hats = model.recognize(inputs, input_length, targets, search)
            
            loss = criterion(preds, targets)
            #loss = criterion(preds[:,:targets.size(1),:].contiguous().view(-1,preds.size(-1)), targets.view(-1))

            losses += loss.item()

            _cer, _wer = metrics(y_hats, targets)
            cer += _cer
            wer += _wer
            step += 1
            pbar.set_description(valid_log.format('valid', epoch, losses/step, cer/step, wer/step))
    logger.info(valid_log.format('valid', epoch, losses/step, cer/step, wer/step))
    
    return losses/step, wer/step