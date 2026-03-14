from Backend.App.Repositories.image_repo import ImageRepo
from Backend.App.Models.image import Image
from Backend.App.logger_config import setup_logger
from Backend.App.Database.connection import connect
from utils.sentinel import DEFAULT

c_r = ImageRepo(setup_logger(), connect("/Users/TimJelenz/Desktop/messenger/Backend/Configurations/mysql.conf", "root"))
v1 = Image(DEFAULT, "Users/TimJelenz/xy", 44)
v2 = Image(DEFAULT, "Users/TimJelenz/xy", 44) 
print(c_r.get_images_path(image_ids=None, post_ids=[44]))
print(c_r.get_images_path(image_ids=[1, 3], post_ids=None))
print(c_r.get_images_path(image_ids=[1, 2], post_ids=[3, 4]))