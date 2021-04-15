from os.path import dirname, basename, isfile
import glob

modules = glob.glob(dirname(__file__)+"/*.py")
__all__ = [basename(f)[:-3] for f in modules if isfile(f)
           and not f.endswith('__init__.py') and not f.endswith('base_model.py')]


# path = 'C:\\Users\\chanq\\OneDrive\\Desktop\\Group3\\backend\\models\\base_model.py'
# print(modules)
# print(basename(path))
# print(basename(path)[:-3])