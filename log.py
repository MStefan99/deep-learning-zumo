# Time correction value is used for compensating the displayed ETA if execution time is nonlinear.
# ETA is multiplied by the correction value, value of 1.0 means no correction.


def log_process(text: str, done: int, total: int, size: int, accuracy=1, info: str = '',
                time_start=0.0, time_now=0.0, time_correction=1.0,
                start='\r', end=''):
    completed = round(done / total * size)
    if time_start and time_now and done > 0:
        seconds = round((time_now - time_start) / done * (total - done) * time_correction)
        if seconds > 60:
            minutes = round(seconds / 60)
            seconds = seconds % 60
            eta = f'ETA: {minutes}m {seconds}s'
        else:
            eta = f'ETA: {seconds}s'
    else:
        eta = ''
    if done == total:
        end = '\n'

    print(f'{start}{text}  [Game {done} of {total}] ' + eta + '  ▌■' +
          '▬' * completed + '►' + ' ' * (size - completed) +
          '▐' + f'  {round(100 * done / total, accuracy)}%.  {info}', end=end)
