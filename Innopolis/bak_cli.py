# ### Задание
#
#
# Ваша цель - создать cli-инструмент, создающий резервную копию папки с файлами.
# Содержание папки и файлов значение не имеет.
# скрипт должен запускаться из терминала, обязательно принимать путь до папки, которую надо заархивировать и путь до папки в которую следует сложить архив.
# в stdout должен возвращаться абсолютный путь до созданного архива.
# Опционально можно указать при запуске программы алгоритм сжатия, по умолчанию gztar.
# Имя архива должно иметь вид: <исходное_название_папки>_<дата_и_время_создания_архива_в_таймзоне_utc>.<расширение>
#
#
# Программа должна вести журнал своего использования, записывая при вызове себя в файл csv или sqlite3 следующую информацию:
# абсолютный путь архивируемой папки, абсолютный путь к созданному архиву (если он был создан), дату и время вызова программы, статус (success или fail) с которым отработала программа.
# Путь до создаваемого журнала вызовов тоже можно задать опционально, по умолчанию файл создаётся в той же директории что и скрипт и имеет название journal.
#
#
# :Опционально: Провальные случаи (например, отсутствие указанной папки или недостаток прав на запись в целевую папку) следует выгружать в stderr
#
#
# Ожидаемый пример использования программы:
# $>python3 app.py --directory /tmp/mydir --output /home/user/alex/ -a zip -j journal.csv
# /home/user/alex/mydir_2020-09-12_04:06:34.zip
#
#
# (создался архив)
# (пополнились записи в файле journal.csv)


import os, shutil, datetime
import logging
import argparse
from logging.handlers import TimedRotatingFileHandler

# формат лога
FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(funcName)s — %(levelname)s — %(message)s")
STATUS_SUCCESS = "SUCCESS!"
STATUS_FAIL = 'FAIL!'


# LOG_FILE = "journal.csv"

# def get_console_handler():
#    console_handler = logging.StreamHandler(sys.stdout)
#    console_handler.setFormatter(FORMATTER)
#    return console_handler
#

# записывает логии в файл
# входной параметр, будущий лог файл
def get_file_handler(log_file: str):
    file_handler = TimedRotatingFileHandler(log_file, when='D', interval=30)
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger(logger_name: str, log_file: str):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)  # better to have too much log than not enough
    # logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler(log_file))
    # with this pattern, it's rarely necessary to propagate the error up to parent
    logger.propagate = False
    return logger


def make_archive(path_from: str, path_to: str, log_file: str, format_arch: str = 'gztar'):
    my_logger = get_logger('bak_cli.make_archive', log_file)
    try:

        if '~' in path_to:
            path_to = os.path.expanduser(path_to)

        if '~' in path_from:
            path_from = os.path.expanduser(path_from)

        date = datetime.datetime.now(datetime.timezone.utc).isoformat(sep='_', timespec='seconds')
        # archive_name = os.path.basename(path_to) + '_' + date
        archive_name = path_to + '_' + date
        result = shutil.make_archive(base_name=archive_name, format=format_arch, root_dir=path_from)
        abs_path_from = os.path.abspath(path_from)
        # l_path_to = os.path.abspath(path_to + '.' + format_arch)
        my_logger.info(f'path of want to archive folder or file {abs_path_from}')
        my_logger.info(f'path of created archive {result}')
        my_logger.info(STATUS_SUCCESS)
        return result

    except FileNotFoundError:
        my_logger.error(f'{path_from} not found')
        my_logger.info(STATUS_FAIL)
        #return f'{path_from} not found'
        return 1

    except Exception:
        my_logger.exception(STATUS_FAIL)
        return 1


def main():
    parser = argparse.ArgumentParser(description='CLI for make archive')
    parser.add_argument('-d', '--directory', required=True, nargs='?', help='The directory that we will archive')
    parser.add_argument('-o', '--output', required=True, nargs='?', help='The directory where we save the archive')
    parser.add_argument('-a', nargs='?', required=True, help='The type of archive: zip, tar, xztar, gztar, bztar')
    parser.add_argument('-j', nargs='?', required=True, help='The journal')
    args = parser.parse_args()
    d = args.directory
    o = args.output
    a = args.a
    j = args.j
    my_logger = get_logger('bak_cli', j)
    my_logger.info('PROGRAM STARTED')
    try:
        result = make_archive(path_from=d, path_to=o, log_file=j, format_arch=a)

        if result != 1:
            print(result)
        else:
            print('ERROR!\n' + 'If you want to know the Еrror, check the log file')
    except Exception:
        my_logger.exception(STATUS_FAIL)
    my_logger.info('DONE\n')



if __name__ == '__main__':
    main()

    # main()

    # path_from = os.path.abspath(path_from)
    # date = datetime.datetime.now(datetime.timezone.utc).isoformat(sep='_',timespec='seconds')
    # archive_name = os.path.basename(path_from) + '_' + date

    # create_archive(path_from,path_to,'zip')
    # shutil.make_archive(base_name=path_to, format='zip',  root_dir=path_from) #правильно работает

    # make_tar(path_from,'test1.tar.gz')
