from controller.SelectorController import SelectorController
from model.SUMImageReader import SUMImageReader

image_reader = SUMImageReader('E:/PythonProjects/SUM_trachea/utilities/experimets/pairing/paired_UCK_lq')
controller = SelectorController(image_reader)

